import asyncio
from typing import List
from PySide6.QtCore import QObject, Signal, QRecursiveMutex, QMutexLocker
from bilibilidownloader.utils import connect_component
from .DownloadWidget import DownloadTask, TaskState


class AsyncTaskQueue(QObject):
    """
    An asynchronous task queue that manages download tasks with asyncio support
    """

    def __init__(self, max_size=None, sorted=False):
        super().__init__()
        self._tasks: List[DownloadTask] = []
        self.max_size = max_size
        self.sorted = sorted
        self._lock = QRecursiveMutex()
        self._loop = None

    def set_event_loop(self, loop):
        """
        Set the asyncio event loop for this queue
        """
        self._loop = loop

    @property
    def is_full(self):
        with QMutexLocker(self._lock):
            return self.max_size is not None and len(self._tasks) == self.max_size

    @property
    def is_empty(self):
        return len(self._tasks) == 0

    @property
    def tasks(self):
        return self._tasks.copy()

    def get_task_index(self, task):
        """
        Get the index of a task in the queue
        """
        try:
            return self._tasks.index(task)
        except ValueError:
            return -1

    def pop(self, task=None, remove=True):
        """
        Remove and return a task from the queue
        """
        with QMutexLocker(self._lock):
            if task is None:
                return self._tasks.pop(0) if self._tasks else None

            index = self.get_task_index(task)
            if index >= 0:
                if remove:
                    return self._tasks.pop(index)
                else:
                    return self._tasks[index]
            return None

    def peek(self, task):
        return self.pop(task, False)

    def push(self, task):
        """
        Add a task to the queue
        """
        with QMutexLocker(self._lock):
            if self.max_size is not None and len(self._tasks) >= self.max_size:
                raise OverflowError(
                    f"TaskQueue is full, max capacity is {self.max_size}"
                )
            task.set_id(len(self._tasks))
            self._tasks.append(task)
            if self.sorted:
                self._tasks.sort(key=lambda x: x.task_id)

    def insert(self, task, pos=-1):
        """
        Insert a task at a specific position
        """
        with QMutexLocker(self._lock):
            if self.max_size is not None and len(self._tasks) >= self.max_size:
                raise OverflowError(
                    f"TaskQueue is full, max capacity is {self.max_size}"
                )

            if pos == -1 or pos >= len(self._tasks):
                self.push(task)
            else:
                self._tasks.insert(pos, task)

    def reid(self, task_id, update=1):
        """
        Re-index tasks after removing a task
        """
        with QMutexLocker(self._lock):
            for task in self._tasks:
                if task.task_id > task_id:
                    task.task_id -= update
            if self.sorted:
                self._tasks.sort(key=lambda x: x.task_id)

    def __iter__(self):
        return iter(self._tasks)

    def __len__(self):
        return len(self._tasks)

    def __contains__(self, task):
        return task in self._tasks

    def __getitem__(self, index):
        return self._tasks[index]


class TaskManager(QObject):
    _cancel_task_occurred = Signal(DownloadTask)

    def __init__(self, max_concurrent=1):
        super().__init__()
        self._paused = AsyncTaskQueue()
        self._pending = AsyncTaskQueue()
        self._running = AsyncTaskQueue(max_size=max_concurrent)
        self._finished = AsyncTaskQueue()
        self._canceled = AsyncTaskQueue(sorted=True)
        self._failed = AsyncTaskQueue()
        self._STATE_Q_MAP = [
            self._failed,
            self._canceled,
            self._finished,
            self._running,
            self._pending,
            self._paused,
        ]
        self._max_task = max
        self._max_concurrent = max_concurrent
        self._event_loop = None
        self._task_manager_task = None
        self._is_running = False

    @property
    def tasks(self):
        """
        Get all tasks in order
        """
        all_tasks = (
            self._failed.tasks
            # + self._canceled.tasks
            + self._finished.tasks
            + self._running.tasks
            + self._pending.tasks
            + self._paused.tasks
        )
        return sorted(all_tasks, key=lambda x: x.task_id)

    def get_task_queue(self, task: DownloadTask):
        """
        Get the queue that corresponds to a task's state
        """
        return self._STATE_Q_MAP[task.status.value + 2]

    def set_event_loop(self, loop):
        """
        Set the asyncio event loop for all queues
        """
        self._event_loop = loop
        for queue in self._STATE_Q_MAP:
            queue.set_event_loop(loop)

    def start(self):
        """
        Start the task manager
        """
        if not self._is_running and self._event_loop:
            self._is_running = True
            self._task_manager_task = asyncio.run_coroutine_threadsafe(
                self._manage_tasks(), self._event_loop
            )

    def stop(self):
        """
        Stop the task manager
        """
        self._is_running = False
        if self._task_manager_task:
            self._task_manager_task.cancel()

    async def _manage_tasks(self):
        """
        Main task management coroutine
        """
        try:
            while self._is_running:
                # Move tasks from pending to running as space becomes available
                while not self._running.is_full and not self._pending.is_empty:
                    task = self._pending.pop()
                    if task:
                        self._running.push(task)
                        # Start the actual download task
                        if hasattr(task, "start_async"):
                            await task.start_async()

                # Check for state changes
                await asyncio.sleep(0.1)  # Small delay to prevent busy looping
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in task management: {e}")

    def add_task(self, task: DownloadTask):
        """
        Add a new task to the manager
        """
        # Connect to task status change signal
        connect_component(
            task.task,
            "_status_change_occurred",
            self._status_change_handler,
        )

        # Add to pending queue if not already there
        if self._pending.get_task_index(task) == -1:
            self._pending.push(task)
            return 1
        return 0

    def _status_change_handler(self, task: DownloadTask, original_status, new_status):
        """
        Handle task status changes
        """
        # Move task between queues based on status change
        original_queue = self._STATE_Q_MAP[original_status.value + 2]
        new_queue = self._STATE_Q_MAP[new_status.value + 2]

        # Remove from original queue
        removed_task = original_queue.pop(task=task)
        if removed_task is not None:
            # Add to new queue
            new_queue.push(task=removed_task)

        # Handle special cases
        if original_status != new_status:
            if new_status == TaskState.CANCELED:
                self._cancel_task_occurred.emit(task)
                self._reindex_tasks(task.task_id)

            # Trigger task management
            if self._event_loop and self._is_running:
                asyncio.run_coroutine_threadsafe(self._manage_tasks(), self._event_loop)

    def _reindex_tasks(self, task_id):
        """
        Re-index all tasks after one is canceled
        """
        for queue in [
            self._failed,
            self._finished,
            self._running,
            self._pending,
            self._paused,
        ]:
            if not queue.sorted:
                queue.reid(task_id)
