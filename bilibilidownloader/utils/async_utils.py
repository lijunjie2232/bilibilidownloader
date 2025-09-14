import asyncio
import functools
from typing import Dict, Any, Callable
from PySide6.QtCore import QMutex, QMutexLocker
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

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
        def wrapper(*args, **kwargs):
            # Get the singleton instance
            pool_manager = PoolManager()

            # Get the pool or raise error if not found
            try:
                pool = pool_manager.get_pool(pool_name)
            except ValueError as e:
                raise ValueError(
                    f"Pool '{pool_name}' not found for function '{func.__name__}'"
                ) from e

            # Handle different pool types
            if asyncio.iscoroutinefunction(func):
                # For async functions, we still need to handle the pool execution
                if isinstance(pool, ThreadPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                elif isinstance(pool, ProcessPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                else:
                    # For custom async pools
                    return func(*args, **kwargs)
            else:
                # For sync functions
                if isinstance(pool, ThreadPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                elif isinstance(pool, ProcessPoolExecutor):
                    loop = asyncio.get_event_loop()
                    return loop.run_in_executor(
                        pool, functools.partial(func, *args, **kwargs)
                    )
                else:
                    # For other pool types, execute directly
                    return func(*args, **kwargs)

        return wrapper

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

# This will raise an error since "nonexistent_pool" is not registered
@concurrent(pool_name="nonexistent_pool")
def another_task():
    pass
"""
