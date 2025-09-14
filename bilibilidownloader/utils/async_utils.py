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
            with QMutexLocker(__POOL_MANAGER_NEW_MUTEX__):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.pools: Dict[str, Any] = {}
            self._initialized = True
            self._op_mutex = QMutex()

    def register_pool(self, name: str, pool: Any):
        """Register a new pool with given name"""
        if name not in self.pools:
            with QMutexLocker(self._op_mutex):
                if name not in self.pools:
                    self.pools[name] = pool

    def get_pool(self, name: str):
        """Get pool by name"""
        if name not in self.pools:
            raise ValueError(
                f"Pool '{name}' not found. Available pools: {list(self.pools.keys())}"
            )
        return self.pools[name]

    def remove_pool(self, name: str):
        """Remove a pool by name"""
        if name in self.pools:
            del self.pools[name]


def get_pool_manager():
    """
    Initialize the pool manager singleton instance
    This should be called during application initialization
    """
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

    def run(self):
        try:
            self._result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self._exception = e

    def result(self):
        if self._exception:
            raise self._exception
        return self._result


class QtAsyncBridge(QObject):
    """
    Bridge for handling Qt thread results in async context
    """

    finished = Signal(object, object)  # result, exception

    def __init__(self):
        super().__init__()

    @Slot()
    def execute_callable(self, wrapper: QtCallableWrapper):
        try:
            result = wrapper.result()
            self.finished.emit(result, None)
        except Exception as e:
            self.finished.emit(None, e)


def concurrent(pool_name: str):
    """
    Decorator to run function concurrently using specified pool

    Args:
        pool_name: Name of the pool to use for concurrent execution

    Raises:
        ValueError: If pool with given name is not found
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the singleton instance
            pool_manager = PoolManager()

            # Get the pool or raise error if not found
            try:
                pool = pool_manager.get_pool(pool_name)
            except ValueError as e:
                raise ValueError(
                    f"Pool '{pool_name}' not found for function '{func.__name__}'"
                ) from e

            # Handle Qt thread pool
            if isinstance(pool, QThreadPool):
                loop = asyncio.get_event_loop()
                future = loop.create_future()

                # Create wrapper for the function
                wrapper = QtCallableWrapper(func, *args, **kwargs)

                # Create bridge to handle result
                bridge = QtAsyncBridge()

                def on_finished(result, exception):
                    if exception:
                        future.set_exception(exception)
                    else:
                        future.set_result(result)

                bridge.finished.connect(on_finished)

                # Execute in Qt thread pool
                pool.start(wrapper)

                # Use QTimer to periodically check if task is done
                def check_result():
                    try:
                        result = wrapper.result()
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
                    except:
                        # If result not ready, check again later
                        QTimer.singleShot(10, check_result)

                QTimer.singleShot(10, check_result)
                return await future

            # Handle different pool types
            elif asyncio.iscoroutinefunction(func):
                # For async functions, we still need to handle the pool execution
                if isinstance(pool, ThreadPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                elif isinstance(pool, ProcessPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                else:
                    # For custom async pools
                    return await func(*args, **kwargs)
            else:
                # For sync functions
                if isinstance(pool, ThreadPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                elif isinstance(pool, ProcessPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                else:
                    # For other pool types, execute directly
                    return func(*args, **kwargs)

        # Preserve the original function for non-async usage
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync usage, we can't really make it async, so we just execute directly
                pool_manager = PoolManager()
                try:
                    pool = pool_manager.get_pool(pool_name)
                except ValueError as e:
                    raise ValueError(
                        f"Pool '{pool_name}' not found for function '{func.__name__}'"
                    ) from e

                # For Qt thread pool in sync context, execute directly
                if isinstance(
                    pool, (QThreadPool, ThreadPoolExecutor, ProcessPoolExecutor)
                ):
                    return func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)

            return sync_wrapper

    return decorator


# During application initialization
pool_manager = get_pool_manager()
pool_manager.register_pool("task_fetch", ThreadPoolExecutor(max_workers=3))

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
