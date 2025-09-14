import asyncio
import functools
from typing import Dict, Any, Callable
from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QThreadPool,
    QRunnable,
    QObject,
    Signal,
    Slot,
)
from PySide6.QtCore import QTimer
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from loguru import logger


__POOL_MANAGER_NEW_MUTEX__ = QMutex()


class PoolManager:
    """
    Singleton class to manage concurrent pools
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            logger.debug("Creating new PoolManager instance")
            with QMutexLocker(__POOL_MANAGER_NEW_MUTEX__):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    logger.debug("PoolManager instance created")
        return cls._instance

    def __init__(self):
        if not self._initialized:
            logger.debug("Initializing PoolManager")
            self.pools: Dict[str, Any] = {}
            self._initialized = True
            self._op_mutex = QMutex()
            logger.debug("PoolManager initialized")

    def register_pool(self, name: str, pool: Any):
        """Register a new pool with given name"""
        logger.debug(f"Attempting to register pool '{name}'")
        if name not in self.pools:
            with QMutexLocker(self._op_mutex):
                if name not in self.pools:
                    self.pools[name] = pool
                    logger.debug(f"Pool '{name}' registered successfully")
                else:
                    logger.debug(f"Pool '{name}' was already registered during lock")
        else:
            logger.debug(f"Pool '{name}' already exists, skipping registration")

    def get_pool(self, name: str):
        """Get pool by name"""
        logger.debug(f"Retrieving pool '{name}'")
        if name not in self.pools:
            error_msg = f"Pool '{name}' not found. Available pools: {list(self.pools.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug(f"Pool '{name}' retrieved successfully")
        return self.pools[name]

    def remove_pool(self, name: str):
        """Remove a pool by name"""
        logger.debug(f"Removing pool '{name}'")
        if name in self.pools:
            del self.pools[name]
            logger.debug(f"Pool '{name}' removed successfully")
        else:
            logger.warning(f"Attempted to remove non-existent pool '{name}'")


def get_pool_manager():
    """
    Initialize the pool manager singleton instance
    This should be called during application initialization
    """
    logger.debug("Getting pool manager instance")
    return PoolManager()


class QtCallableWrapper(QRunnable):
    """
    Wrapper for running Python callables in Qt threads
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._result = None
        self._exception = None
        logger.debug(f"QtCallableWrapper created for function '{func.__name__}'")

    def run(self):
        logger.debug(f"Executing function '{self.func.__name__}' in Qt thread")
        try:
            self._result = self.func(*self.args, **self.kwargs)
            logger.debug(f"Function '{self.func.__name__}' executed successfully in Qt thread")
        except Exception as e:
            self._exception = e
            logger.error(f"Exception in Qt thread execution of '{self.func.__name__}': {e}")

    def result(self):
        logger.debug(f"Retrieving result for function '{self.func.__name__}'")
        if self._exception:
            logger.error(f"Result retrieval failed for '{self.func.__name__}' due to exception: {self._exception}")
            raise self._exception
        logger.debug(f"Result retrieved successfully for '{self.func.__name__}'")
        return self._result


class QtAsyncBridge(QObject):
    """
    Bridge for handling Qt thread results in async context
    """

    finished = Signal(object, object)  # result, exception

    def __init__(self):
        super().__init__()
        logger.debug("QtAsyncBridge created")

    @Slot()
    def execute_callable(self, wrapper: QtCallableWrapper):
        logger.debug("Executing callable in QtAsyncBridge")
        try:
            result = wrapper.result()
            logger.debug("Callable executed successfully in QtAsyncBridge")
            self.finished.emit(result, None)
        except Exception as e:
            logger.error(f"Exception in QtAsyncBridge execution: {e}")
            self.finished.emit(None, e)


def concurrent(pool_name: str):
    """
    Decorator to run function concurrently using specified pool

    Args:
        pool_name: Name of the pool to use for concurrent execution

    Raises:
        ValueError: If pool with given name is not found
    """
    logger.debug(f"Creating concurrent decorator for pool '{pool_name}'")

    def decorator(func: Callable):
        logger.debug(f"Applying concurrent decorator to function '{func.__name__}' with pool '{pool_name}'")
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.debug(f"Executing async wrapper for '{func.__name__}' with pool '{pool_name}'")
            # Get the singleton instance
            pool_manager = PoolManager()

            # Get the pool or raise error if not found
            try:
                pool = pool_manager.get_pool(pool_name)
                logger.debug(f"Pool '{pool_name}' acquired for function '{func.__name__}'")
            except ValueError as e:
                logger.error(f"Pool '{pool_name}' not found for function '{func.__name__}': {e}")
                raise ValueError(
                    f"Pool '{pool_name}' not found for function '{func.__name__}'"
                ) from e

            # Handle Qt thread pool
            if isinstance(pool, QThreadPool):
                logger.debug(f"Using QtThreadPool for function '{func.__name__}'")
                loop = asyncio.get_event_loop()
                future = loop.create_future()

                # Create wrapper for the function
                wrapper = QtCallableWrapper(func, *args, **kwargs)
                logger.debug(f"QtCallableWrapper created for '{func.__name__}'")

                # Create bridge to handle result
                bridge = QtAsyncBridge()
                logger.debug(f"QtAsyncBridge created for '{func.__name__}'")

                def on_finished(result, exception):
                    logger.debug(f"QtAsyncBridge finished signal received for '{func.__name__}'")
                    if exception:
                        logger.error(f"Exception in Qt execution of '{func.__name__}': {exception}")
                        future.set_exception(exception)
                    else:
                        logger.debug(f"Qt execution of '{func.__name__}' completed successfully")
                        future.set_result(result)

                bridge.finished.connect(on_finished)

                # Execute in Qt thread pool
                pool.start(wrapper)
                logger.debug(f"Function '{func.__name__}' submitted to Qt thread pool")

                # Use QTimer to periodically check if task is done
                def check_result():
                    logger.debug(f"Checking result for '{func.__name__}'")
                    try:
                        result = wrapper.result()
                        logger.debug(f"Result obtained for '{func.__name__}', setting future result")
                        future.set_result(result)
                    except Exception as e:
                        logger.error(f"Exception in result checking for '{func.__name__}': {e}")
                        future.set_exception(e)
                    except:
                        # If result not ready, check again later
                        logger.debug(f"Result not ready for '{func.__name__}', scheduling next check")
                        QTimer.singleShot(10, check_result)

                QTimer.singleShot(10, check_result)
                result = await future
                logger.debug(f"Async wrapper completed for '{func.__name__}' with QtThreadPool")
                return result

            # Handle different pool types
            elif asyncio.iscoroutinefunction(func):
                logger.debug(f"Handling async function '{func.__name__}' with pool '{pool_name}'")
                # For async functions, we still need to handle the pool execution
                if isinstance(pool, ThreadPoolExecutor):
                    logger.debug(f"Using ThreadPoolExecutor for async function '{func.__name__}'")
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                    logger.debug(f"ThreadPoolExecutor execution completed for '{func.__name__}'")
                    return result
                elif isinstance(pool, ProcessPoolExecutor):
                    logger.debug(f"Using ProcessPoolExecutor for async function '{func.__name__}'")
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                    logger.debug(f"ProcessPoolExecutor execution completed for '{func.__name__}'")
                    return result
                else:
                    # For custom async pools
                    logger.debug(f"Using custom pool for async function '{func.__name__}'")
                    result = await func(*args, **kwargs)
                    logger.debug(f"Custom pool execution completed for '{func.__name__}'")
                    return result
            else:
                # For sync functions
                logger.debug(f"Handling sync function '{func.__name__}' with pool '{pool_name}'")
                if isinstance(pool, ThreadPoolExecutor):
                    logger.debug(f"Using ThreadPoolExecutor for sync function '{func.__name__}'")
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                    logger.debug(f"ThreadPoolExecutor execution completed for '{func.__name__}'")
                    return result
                elif isinstance(pool, ProcessPoolExecutor):
                    logger.debug(f"Using ProcessPoolExecutor for sync function '{func.__name__}'")
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                    logger.debug(f"ProcessPoolExecutor execution completed for '{func.__name__}'")
                    return result
                else:
                    # For other pool types, execute directly
                    logger.debug(f"Executing function '{func.__name__}' directly")
                    result = func(*args, **kwargs)
                    logger.debug(f"Direct execution completed for '{func.__name__}'")
                    return result

        # Preserve the original function for non-async usage
        if asyncio.iscoroutinefunction(func):
            logger.debug(f"Returning async wrapper for coroutine function '{func.__name__}'")
            return async_wrapper
        else:
            logger.debug(f"Creating sync wrapper for function '{func.__name__}'")

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                logger.debug(f"Executing sync wrapper for '{func.__name__}' with pool '{pool_name}'")
                # For sync usage, we can't really make it async, so we just execute directly
                pool_manager = PoolManager()
                try:
                    pool = pool_manager.get_pool(pool_name)
                    logger.debug(f"Pool '{pool_name}' acquired for sync function '{func.__name__}'")
                except ValueError as e:
                    logger.error(f"Pool '{pool_name}' not found for sync function '{func.__name__}': {e}")
                    raise ValueError(
                        f"Pool '{pool_name}' not found for function '{func.__name__}'"
                    ) from e

                # For Qt thread pool in sync context, execute directly
                if isinstance(
                    pool, (QThreadPool, ThreadPoolExecutor, ProcessPoolExecutor)
                ):
                    logger.debug(f"Executing '{func.__name__}' with supported pool type {type(pool).__name__}")
                    result = func(*args, **kwargs)
                    logger.debug(f"Execution completed for '{func.__name__}' with supported pool")
                    return result
                else:
                    logger.debug(f"Executing '{func.__name__}' directly")
                    result = func(*args, **kwargs)
                    logger.debug(f"Direct execution completed for '{func.__name__}'")
                    return result

            logger.debug(f"Returning sync wrapper for function '{func.__name__}'")
            return sync_wrapper

    logger.debug(f"Concurrent decorator created for pool '{pool_name}'")
    return decorator


# During application initialization
logger.debug("Initializing pool manager")
pool_manager = get_pool_manager()
pool_manager.register_pool("task_fetch", ThreadPoolExecutor(max_workers=3))
logger.debug("Pool manager initialization completed")

"""
# Using the decorator
@concurrent(pool_name="io_pool")
async def fetch_data(url):
    # Some async I/O operation
    pass

@concurrent(pool_name="cpu_pool")
def cpu_intensive_task(data):
    # Some CPU intensive operation
    pass

@concurrent(pool_name="qt_pool")
def qt_thread_task(data):
    # Task to run in Qt thread
    pass

# This will raise an error since "nonexistent_pool" is not registered
@concurrent(pool_name="nonexistent_pool")
def another_task():
    pass
"""