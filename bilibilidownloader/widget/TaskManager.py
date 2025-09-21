import asyncio
import time
from functools import partial
from traceback import print_stack
from typing import List

from loguru import logger
from PySide6.QtCore import QMutexLocker, QObject, QRecursiveMutex, QThread, Signal

from bilibilicore.config import Config

from bilibilidownloader.utils import connect_component

from .DownloadWidget import DownloadTaskWidget, TaskOp, TaskState


class AsyncTaskQueue(QObject):
    """
    An asynchronous task queue that manages download tasks with asyncio support
    """

    def __init__(self, max_size=None, sorted=False):
        super().__init__()
        self._tasks: List[DownloadTaskWidget] = []
        self.max_size = max_size
        self.sorted = sorted
        self._lock = QRecursiveMutex()
        self._loop = None

    # def set_event_loop(self, loop):
    #     """
    #     Set the asyncio event loop for this queue
    #     """
    #     self._loop = loop

    @property
    def is_full(self):
        with QMutexLocker(self._lock):
            return self.max_size is not None and len(self._tasks) == self.max_size

    @property
    def is_empty(self):
        return len(self._tasks) == 0
    
    @property
    def size(self):
        return len(self._tasks)
    
    def full_at(self, length):
        return len(self._tasks) >= length

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
            # task.set_id(len(self._tasks))
            self._tasks.append(task)
            if self.sorted:
                self._tasks.sort(key=lambda x: x.id)

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
                if task.id > task_id:
                    task.id -= update
            if self.sorted:
                self._tasks.sort(key=lambda x: x.id)

    def __iter__(self):
        return iter(self._tasks)

    def __len__(self):
        return len(self._tasks)

    def __contains__(self, task):
        return task in self._tasks

    def __getitem__(self, index):
        return self._tasks[index]


class TaskManager(QObject):
    _cancel_task_occurred = Signal(DownloadTaskWidget)
    _task_finished_occurred = Signal()

    def __init__(self):
        super().__init__()
        self._paused = AsyncTaskQueue()
        self._pending = AsyncTaskQueue()
        self._running = AsyncTaskQueue()
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
        # self._max_concurrent = max_concurrent
        self._event_loop = None
        self._task_manager_task = None
        self._is_running = False
        self._manager_lock = QRecursiveMutex()  # Add lock for TaskManager
        self._init_manager()

    @property
    def tasks(self):
        """
        Get all tasks in order
        """
        with QMutexLocker(self._manager_lock):
            all_tasks = (
                self._failed.tasks
                # + self._canceled.tasks
                + self._finished.tasks
                + self._running.tasks
                + self._pending.tasks
                + self._paused.tasks
            )
            return sorted(all_tasks, key=lambda x: x.id)

    def _init_manager(self):
        """
        Initialize and start the task manager thread
        """
        self._task_manager_task = TaskManagerThread(self)
        self._task_manager_task.start()
        self._is_running = True

    def get_task_queue(self, task: DownloadTaskWidget):
        """
        Get the queue that corresponds to a task's state
        """
        with QMutexLocker(self._manager_lock):
            return self._STATE_Q_MAP[task.status.value + 2]

    # def set_event_loop(self, loop):
    #     """
    #     Set the asyncio event loop for all queues
    #     """
    #     with QMutexLocker(self._manager_lock):
    #         self._event_loop = loop
    #         for queue in self._STATE_Q_MAP:
    #             queue.set_event_loop(loop)

    def start_manager(self):
        """
        Start the task manager
        """
        with QMutexLocker(self._manager_lock):
            if not self._is_running and self._event_loop:
                self._is_running = True
                self._task_manager_task = asyncio.run_coroutine_threadsafe(
                    self._manage_tasks(), self._event_loop
                )

    def stop_manager(self):
        """
        Stop the task manager
        """
        with QMutexLocker(self._manager_lock):
            self._is_running = False
            if self._task_manager_task:
                self._task_manager_task.cancel()

    async def _manage_tasks(self):
        """
        Main task management coroutine
        """
        while self._is_running:
            try:
                # Move tasks from pending to running as space becomes available
                if not self._running.full_at(Config().download.parallel) and not self._pending.is_empty:
                    with QMutexLocker(self._manager_lock):
                        while not self._running.full_at(Config().download.parallel) and not self._pending.is_empty:
                            task_widget = self._pending.pop()
                            if task_widget:
                                assert task_widget.status == TaskState.PENDING
                                # Set task status to RUNNING
                                task_widget.set_status(TaskState.RUNNING, emit=False)
                                self._pending.push(task_widget)
                                # Start the actual download task
                                task_widget.task.start()

                # Check for state changes
                await asyncio.sleep(1)  # Small delay to prevent busy looping
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error in task management: {e}")

    def add_task(self, task: DownloadTaskWidget):
        """
        Add a new task to the manager
        """
        with QMutexLocker(self._manager_lock):
            # Connect to task status change signal
            connect_component(
                task,
                "_status_change_occurred",
                partial(self._status_change_handler, task),
            )
            connect_component(
                task,
                "_op_occured",
                partial(self._op_handler, task),
            )

            # Add to pending queue if not already there
            if self._pending.get_task_index(task) == -1:
                self._pending.push(task)
                return 1
            return 0

    def _op_handler(self, task: DownloadTaskWidget, op: TaskOp):
        with QMutexLocker(self._manager_lock):
            with QMutexLocker(task.status_mutex):
                if task.status.value == op.value:
                    return
                task.set_status(TaskState(op.value))

    def _status_change_handler(
        self, task: DownloadTaskWidget, original_status, new_status
    ):
        """
        Handle task status changes
        """
        with QMutexLocker(self._manager_lock):
            if isinstance(original_status, int):
                original_status = TaskState(original_status)
            if isinstance(new_status, int):
                new_status = TaskState(new_status)
            if original_status == new_status:
                return
            # Move task between queues based on status change
            original_queue = self._STATE_Q_MAP[original_status.value + 2]
            new_queue = self._STATE_Q_MAP[new_status.value + 2]

            # Remove from original queue
            removed_task = original_queue.pop(task=task)
            if removed_task is not None:
                # Add to new queue
                new_queue.push(task=removed_task)

            # If task is finished, stopped or failed, stop the download thread
            if new_status in [TaskState.PAUSED, TaskState.CANCELED]:
                task.task.stop()

            # Handle special cases
            if new_status == TaskState.CANCELED:
                self._cancel_task_occurred.emit(task)
                self._take_task(task)

            if new_status == TaskState.FINISHED:
                self._task_finished_occurred.emit()

            logger.debug(
                f"Task {task.id} status changed to {new_status} from {original_status}"
            )

    def _take_task(self, task: DownloadTaskWidget):
        """
        Take a task out of the manager
        """
        if task not in self._canceled:
            return
        self._canceled.pop(task)
        self._reindex_tasks(task.id)

    def _reindex_tasks(self, task_id):
        """
        Re-index all tasks after one is canceled
        """
        with QMutexLocker(self._manager_lock):
            for queue in [
                self._failed,
                self._finished,
                self._running,
                self._pending,
                self._paused,
            ]:
                if not queue.sorted:
                    queue.reid(task_id)

    @property
    def is_running(self):
        with QMutexLocker(self._manager_lock):
            return self._is_running

    @property
    def pending(self):
        with QMutexLocker(self._manager_lock):
            return self._pending

    @property
    def running(self):
        with QMutexLocker(self._manager_lock):
            return self._running


class TaskManagerThread(QThread):
    def __init__(self, task_manager):
        super().__init__()
        self.task_manager = task_manager

    def run(self):
        """
        Run the task management loop
        """
        while self.task_manager._is_running:
            try:
                # Move tasks from pending to running as space becomes available
                if (
                    not self.task_manager.running.is_full
                    and not self.task_manager.pending.is_empty
                ):
                    with QMutexLocker(self.task_manager._manager_lock):
                        while not (
                            self.task_manager.running.is_full
                            or self.task_manager.pending.is_empty
                        ):
                            task_widget = self.task_manager.pending.pop()
                            if task_widget:
                                assert task_widget.status == TaskState.PENDING
                                # Set task status to RUNNING
                                task_widget.set_status(
                                    TaskState.RUNNING,
                                    emit=False,
                                )
                                self.task_manager.running.push(task_widget)
                                # Start the actual download task
                                task_widget.task.start()
            except Exception as e:
                print(f"Error in task management: {e}")
            finally:
                # Check for state changes
                time.sleep(1)  # Small delay to prevent busy looping
