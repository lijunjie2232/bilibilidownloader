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

    def get_task_queue(
        self,
        task: DownloadTask,
    ):
        return self._STATE_Q_MAP[task.status.value + 2]

    def add_task(
        self,
        task: DownloadTask,
    ):
        """
        添加任务。
        """

        connect_component(
            task.task,
            "_status_change_occurred",
            self.status_change_occurred_handler,
        )
        # q = self.get_task_queue(task)
        with QMutexLocker(self._lock):
            if self._pending.get_task(task) != -1:
                return 0
            else:
                self._pending.push(task)
                task.start()
                return 1
                # todo push add condition
        self.running_task_manage()

    @thread
    def status_change_occurred_handler(
        self,
        task: DownloadTask,
        original_status,
        new_status,
    ):
        with QMutexLocker(self._lock):
            t = self._STATE_Q_MAP[original_status.value + 2].pop(task=task)
            assert t is not None
            self._STATE_Q_MAP[new_status.value + 2].push(task=t)

        if original_status == new_status:
            return
        elif new_status == TaskState.CANCELED:
            self._cancel_task_occurred.emit(task)
            self.reid(task.task_id)
        self.running_task_manage()

    @thread
    def running_task_manage(self):
        try:
            if self._running.is_full:
                return
            with QMutexLocker(self._lock):
                while not self._running.is_full and not self._pending.is_empty:
                    self._running.push(self._pending.pop())
            for task in self._running:
                # task.start()
                task.task.start_task()
        except:
            pass

    def reid(self, task_id):
        with QMutexLocker(self._lock):
            for q in [
                self._failed,
                self._finished,
                self._running,
                self._pending,
                self._paused,
            ]:
                if not q.sorted:
                    q.reid(task_id)
