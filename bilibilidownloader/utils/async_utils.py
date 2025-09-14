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
            error_msg = (
                f"Pool '{name}' not found. Available pools: {list(self.pools.keys())}"
            )
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


# During application initialization
logger.debug("Initializing pool manager")
pool_manager = get_pool_manager()
pool_manager.register_pool("task_fetch", ThreadPoolExecutor(max_workers=2))
logger.debug("Pool manager initialization completed")


def concurrent(pool_name: str):
    """
    Decorator to run function in concurrent thread.
    If pool not found, raise error.

    Args:
        pool_name: Name of the pool to use for execution
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the pool manager instance
            manager = get_pool_manager()

            # Try to get the specified pool
            try:
                pool = manager.get_pool(pool_name)
            except ValueError as e:
                logger.error(
                    f"Pool '{pool_name}' not found when executing '{func.__name__}': {e}"
                )
                raise

            # # Check if function is async
            # if asyncio.iscoroutinefunction(func):
            #     # For async functions, submit to the pool and return awaitable
            #     future = pool.submit(func, *args, **kwargs)
            #     return future
            # else:
            #     # For sync functions, submit to the pool
            #     future = pool.submit(func, *args, **kwargs)
            #     return future.result()
            pool.submit(func, *args, **kwargs)

        return wrapper

    return decorator


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
