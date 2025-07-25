import math
from pathlib import Path
from traceback import print_exc
from shutil import move, rmtree
import requests
from bilibilicore.api import DashStream
from bilibilicore.config import Config
from bilibilicore.utils import clean_tmp, combine
from PySide6.QtCore import (
    QFile,
    QIODevice,
    QMutex,
    QMutexLocker,
    QObject,
    QRecursiveMutex,
    QSize,
    Qt,
    QThread,
    QUrl,
    QWaitCondition,
    Signal,
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLabel, QProgressBar, QWidget

from bilibilidownloader.ui import __MODULE_PATH__, Ui_DownloadTask
from bilibilidownloader.utils import (
    connect_component,
    load_image_to_label,
    thread,
    copy_session,
)

from .AnalyzerWidget import AnalyzeTask

_CHUNK_SIZE = 1024 * 64
_ICON_SIZE = QSize(16, 16)

from enum import Enum, unique


@unique
class TaskState(Enum):
    """Docstring for MyEnum."""

    FAILED = -2
    CANCELED = -1
    FINISHED = 0
    RUNNING = 1
    PENDING = 2
    PAUSED = 3


class DownloadTaskWidget(QWidget, Ui_DownloadTask):
    __CONFIG__ = Config()
    __SESSION__ = copy_session(__CONFIG__.session)
    _status_change_occurred = Signal(object, TaskState, TaskState)

    _update_status_label = Signal(str)  # 用于更新 QLabel 的文本
    _update_progress_bar = Signal(int, int)  # 用于更新进度条

    def __init__(
        self,
        task: AnalyzeTask,
        save_dir,
        id,
    ):
        super(DownloadTaskWidget, self).__init__()
        # self.ui = Ui_DownloadTask()
        # self.ui.setupUi(self)
        self.setupUi(self)

        self._task = task
        self._save_dir = Path(save_dir)
        if self._task.vname and Config().download.auto_create_album_dir:
            self._save_dir /= self._task.vname
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._id = id

        self._video: DashStream = self._task.selected_video
        self._audio: DashStream = self._task.selected_audio
        self._filename = self.filename_gen()

        self._status = TaskState.PENDING
        # self._status_mutex = QMutex()
        self._status_mutex = QRecursiveMutex()
        self._condition = QWaitCondition()
        self._event_loop = None

        self.resume_icon = None
        self.pause_icon = None
        self.cancel_icon = None
        self.icon_init()

        # 初始化控件
        self.id_label.setText(str(id) if id > -1 else "")
        self.title_label.setText(task.title)
        self.vname_label.setText(task.vname)
        self.quality_label.setText(task.quality_str)
        self.duration_label.setText(task.duration_str)
        self.progress_bar.setValue(0)
        connect_component(
            self.cancel_btn,
            "clicked",
            self.cancel_handler,
        )
        connect_component(
            self.pause_or_resume_btn,
            "clicked",
            self.pause_or_resume_handler,
        )

        connect_component(
            self.debug_btn,
            "clicked",
            self.debug_handler,
        )

        self._update_status_label.connect(self.status_label.setText)
        self._update_progress_bar.connect(self.update_progress)

        # 设置缩略图
        if task.img or task.pic_url:
            load_image_to_label(
                self.thumbnail_label,
                url=task.pic_url,
                img=task.img,
            )
        else:
            self.thumbnail_label.setText("No Image")

        self.pend()

    def set_event_loop(self, loop):
        """
        Set the asyncio event loop for this task widget
        """
        self._event_loop = loop

    def debug_handler(self):
        pass

    @property
    def task(self):
        return self._task

    def icon_init(self):
        self.resume_icon = QIcon()
        self.pause_icon = QIcon()
        self.cancel_icon = QIcon()
        self.resume_icon.addFile(
            ":/icon/bilibilidownloader/ui/assert/resume.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.On,
        )
        self.pause_icon.addFile(
            ":/icon/bilibilidownloader/ui/assert/pause.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.On,
        )
        self.cancel_icon.addFile(
            ":/icon/bilibilidownloader/ui/assert/cancel.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.On,
        )
        self.cancel_btn.setIcon(self.cancel_icon)
        self.cancel_btn.setIconSize(_ICON_SIZE)
        self.pause_or_resume_btn.setIcon(self.pause_icon)
        self.pause_or_resume_btn.setIconSize(_ICON_SIZE)

    @property
    def session(self) -> requests.Session:
        return self.__SESSION__

    def filename_gen(self):
        width = math.ceil(math.log10(self._task.total))

        # 使用 f-string 补零
        padded_id = str(self._id).rjust(width, "0")

        return f"{padded_id}_{self._task.title}"

    def set_id(self, id):
        self._id = id
        self.id_label.setText(str(id + 1))

    @property
    def status(self):
        return self._status

    @property
    def status_mutex(self):
        return self._status_mutex

    def resume(
        self,
        emit=False,
    ):
        with QMutexLocker(self._status_mutex):
            if not self._status == TaskState.PAUSED:
                return
            self._set_status(
                TaskState.PENDING,
                emit=emit,
            )
            self.pause_or_resume_btn.setIcon(self.pause_icon)
            self._condition.wakeAll()

    def pause(
        self,
        emit=False,
    ):
        with QMutexLocker(self._status_mutex):
            if self._status not in (
                TaskState.PENDING,
                TaskState.RUNNING,
            ):
                return
            self._set_status(
                TaskState.PAUSED,
                emit=emit,
            )
            self.pause_or_resume_btn.setIcon(self.resume_icon)

    def cancel(
        self,
        emit=False,
    ):
        with QMutexLocker(self._status_mutex):
            if self._status in (TaskState.CANCELED, TaskState.FINISHED):
                return
            else:
                self._set_status(
                    TaskState.CANCELED,
                    emit=emit,
                )
            self._condition.wakeAll()

    def pend(
        self,
        emit=False,
    ):
        with QMutexLocker(self._status_mutex):
            if self._status == TaskState.PENDING:
                return
            self._set_status(
                TaskState.PENDING,
                emit=emit,
            )

    @thread
    def pause_or_resume_handler(self):
        print(self._status)
        with QMutexLocker(self._status_mutex):
            if self._status == TaskState.PAUSED:
                self.resume(emit=True)
            elif self._status in (
                TaskState.PENDING,
                TaskState.RUNNING,
            ):
                self.pause(emit=True)

    async def start_task_async(self, emit=False):
        """
        Async version of start_task
        """
        print(self._status)
        with QMutexLocker(self._status_mutex):
            self._set_status(
                TaskState.RUNNING,
                emit=emit,
            )
            self._condition.wakeAll()

    @thread
    def start_task(self, emit=False):
        """
        Synchronous version of start_task for backward compatibility
        """
        print(self._status)
        with QMutexLocker(self._status_mutex):
            self._set_status(
                TaskState.RUNNING,
                emit=emit,
            )
            self._condition.wakeAll()

    @thread
    def cancel_handler(self):
        print(self._status)
        self.cancel()

    def _set_status(
        self,
        status: TaskState,
        emit=True,
    ):
        origin_status = self._status
        self._status = status
        if origin_status != status and emit:
            self._status_change_occurred.emit(
                self,
                origin_status,
                self._status,
            )
        return origin_status

    def update_progress(self, downloaded: int, total: int):
        if not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
        self.progress_bar.setValue(downloaded)
        if self.progress_bar.maximum() != total:
            self.progress_bar.setMaximum(total)

    def signal_check(self) -> bool:
        """
        检查当前是否处于暂停或停止状态。

        :return: 如果应继续下载返回 True，否则返回 False。
        """
        with QMutexLocker(self._status_mutex):
            while self._status != TaskState.RUNNING:
                if self._status == TaskState.PAUSED:
                    origin_text = self.status_label.text()
                    # self.status_label.setText("已暂停...")
                    self._update_status_label.emit("已暂停...")
                    self._condition.wait(self._status_mutex)
                    # self.status_label.setText(origin_text)
                    self._update_status_label.emit(origin_text)
                elif self._status == TaskState.PENDING:
                    origin_text = self.status_label.text()
                    # self.status_label.setText("队列中...")
                    self._update_status_label.emit("队列中...")
                    self._condition.wait(self._status_mutex)
                    # self.status_label.setText(origin_text)
                    self._update_status_label.emit(origin_text)
                else:
                    return False
            return self._status == TaskState.RUNNING
    async def async_download_file(
        self,
        url: str,
        backup_url: str = None,
        output_path: str = "./output.mp4",
        desc: str = "file",
        overwrite: bool = False,
    ) -> bool:
        """
        Async version of download_file using aiohttp with niquests-style headers and cookies
        """
        final_file_path = Path(output_path)
        if final_file_path.exists() and not overwrite:
            return True
        output_path = final_file_path.parent / f"{final_file_path.name}.tmp"
        url_list = [url]
        if backup_url:
            url_list.append(backup_url)
            
        # Extract headers and cookies from the existing requests session
        session_headers = dict(self.session.headers)
        session_cookies = dict(self.session.cookies)
        
        for attempt, current_url in enumerate(url_list, start=1):
            if not self.signal_check():
                return False
            try:
                # Create aiohttp session with headers and cookies from niquests session
                timeout = aiohttp.ClientTimeout(total=30)
                connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
                
                async with aiohttp.ClientSession(
                    headers=session_headers,
                    cookies=session_cookies,
                    timeout=timeout,
                    connector=connector
                ) as session:
                    async with session.head(current_url) as head_response:
                        total_size = int(
                            head_response.headers.get(
                                "Content-Length",
                                0,
                            )
                        )

                    # 获取已下载大小（断点续传基础）
                    downloaded = 0
                    mode = "ab" if output_path.exists() else "wb"
                    file_size = output_path.stat().st_size if mode == "ab" else 0
                    downloaded = file_size

                    self.update_progress(file_size, total_size)

                    if file_size == total_size:
                        move(output_path, final_file_path)
                        return True

                    # Prepare headers for the download request
                    download_headers = session_headers.copy()
                    if file_size > 0:
                        download_headers["Range"] = f"bytes={file_size}-"

                    async with session.get(
                        current_url,
                        headers=download_headers,
                        timeout=timeout,
                    ) as response:
                        response.raise_for_status()
                        
                        total = int(response.headers.get("Content-Length", 0))
                        if file_size > 0:
                            total += file_size
                        
                        with open(output_path, mode) as f:
                            async for chunk in response.content.iter_chunked(_CHUNK_SIZE):
                                # 写入数据
                                f.write(chunk)
                                downloaded += len(chunk)

                                if not self.signal_check():
                                    f.close()
                                    return False

                                # 更新进度条
                                self.update_progress(downloaded, total)
                
                move(output_path, final_file_path)
                return True  # 成功下载

            except Exception as e:
                if attempt == 1 and backup_url:
                    continue  # 尝试备用链接
                else:
                    print(f"无法下载 {desc}：{e}", level="error")
                    return False

    async def run_async(self):
        """
        Async version of run method
        """
        if self._status in (
            TaskState.CANCELED,
            TaskState.FINISHED,
            TaskState.RUNNING,
        ):
            return
        with QMutexLocker(self._status_mutex):
            if self._status in (
                TaskState.CANCELED,
                TaskState.FINISHED,
                TaskState.RUNNING,
            ):
                return
            self._status = TaskState.RUNNING

        self._update_status_label.emit("正在分析...")

        video = self._video["stream"]
        audio = self._audio["stream"] if self._audio else None
        assert isinstance(video, DashStream), NotImplementedError()
        assert audio is None or isinstance(audio, DashStream), NotImplementedError()
        ori_vfmt = "m4s"
        ori_afmt = "m4s"
        if len(video.base_url.split("?")[0].split(".")) > 2:
            ori_vfmt = video.base_url.split("?")[0].split(".")[-1]
        if len(audio.base_url.split("?")[0].split(".")) > 2:
            ori_afmt = audio.base_url.split("?")[0].split(".")[-1]
        tmp_video_path = self._save_dir / f"{self._filename}_v.{ori_vfmt}"
        tmp_audio_path = self._save_dir / f"{self._filename}_a.{ori_afmt}"
        out_path = self._save_dir / f"{self._filename}.{self._task.fmt}"

        if out_path.exists():
            self.set_finish(True)
            return
        tmp_out_path = self._save_dir / f"{out_path.stem}_tmp.{out_path.suffix}"

        self._update_status_label.emit("正在下载视频")

        if not self.signal_check():
            return

        result = await self.async_download_file(
            url=video.base_url,
            backup_url=video.backup_url,
            output_path=tmp_video_path,
            desc="video",
        )
        if not result:
            self._update_status_label.emit("下载视频失败或取消")

        elif audio:
            self._update_status_label.emit("正在下载音频")
            result = await self.async_download_file(
                url=audio.base_url,
                backup_url=audio.backup_url,
                output_path=tmp_audio_path,
                desc="audio",
            )
            if not result:
                self._update_status_label.emit("下载音频失败或取消")
            else:
                self._update_status_label.emit("正在合并文件")
                if not self.signal_check():
                    return
                combine(
                    v=tmp_video_path,
                    a=tmp_audio_path,
                    out_file=tmp_out_path,
                    fmt=None if self._task.fmt != ori_vfmt else None,
                    overwrite=True,
                )
                move(tmp_out_path, out_path)

        self._update_status_label.emit("缓存清理")
        clean_tmp(
            tmp_video_path,
            tmp_audio_path,
        )
        self.set_finish(result)
    def run(self):
        if self._status in (
            TaskState.CANCELED,
            TaskState.FINISHED,
            TaskState.RUNNING,
        ):
            return
        with QMutexLocker(self._status_mutex):
            if self._status in (
                TaskState.CANCELED,
                TaskState.FINISHED,
                TaskState.RUNNING,
            ):
                return
            self._status = TaskState.RUNNING

        # self.status_label.setText("正在分析...")
        self._update_status_label.emit("正在分析...")

        video = self._video["stream"]
        audio = self._audio["stream"] if self._audio else None
        assert isinstance(video, DashStream), NotImplementedError()
        assert audio is None or isinstance(audio, DashStream), NotImplementedError()
        ori_vfmt = "m4s"
        ori_afmt = "m4s"
        if len(video.base_url.split("?")[0].split(".")) > 2:
            ori_vfmt = video.base_url.split("?")[0].split(".")[-1]
        if len(audio.base_url.split("?")[0].split(".")) > 2:
            ori_afmt = audio.base_url.split("?")[0].split(".")[-1]
        tmp_video_path = self._save_dir / f"{self._filename}_v.{ori_vfmt}"
        tmp_audio_path = self._save_dir / f"{self._filename}_a.{ori_afmt}"
        out_path = self._save_dir / f"{self._filename}.{self._task.fmt}"

        if out_path.exists():
            self.set_finish(True)
            return
        tmp_out_path = self._save_dir / f"{out_path.stem}_tmp.{out_path.suffix}"

        # self.status_label.setText("正在下载视频")
        self._update_status_label.emit("正在下载视频")

        if not self.signal_check():
            return

        result = self.download_file(
            url=video.base_url,
            backup_url=video.backup_url,
            output_path=tmp_video_path,
            desc="video",
        )
        if not result:
            # self.status_label.setText("下载视频失败或取消")
            self._update_status_label.emit("下载视频失败或取消")

        elif audio:
            # self.status_label.setText("正在下载音频")
            self._update_status_label.emit("正在下载音频")
            result = self.download_file(
                url=audio.base_url,
                backup_url=audio.backup_url,
                output_path=tmp_audio_path,
                desc="audio",
            )
            if not result:
                # self.status_label.setText("下载音频失败或取消")
                self._update_status_label.emit("下载音频失败或取消")
            else:
                # self.status_label.setText("正在合并文件")
                self._update_status_label.emit("正在合并文件")
                if not self.signal_check():
                    return
                combine(
                    v=tmp_video_path,
                    a=tmp_audio_path,
                    out_file=tmp_out_path,
                    fmt=None if self._task.fmt != ori_vfmt else None,
                    overwrite=True,
                )
                move(tmp_out_path, out_path)

        # self.status_label.setText("清理缓存")
        self._update_status_label.emit("缓存清理")
        clean_tmp(
            tmp_video_path,
            tmp_audio_path,
        )
        self.set_finish(result)

    def set_finish(self, result):
        with QMutexLocker(self._status_mutex):
            if result:
                self._status = TaskState.FINISHED
                self.progress_bar.setValue(self.progress_bar.maximum())
                # self.status_label.setText("下载完成")
                self._update_status_label.emit("下载完成")
            else:
                self._status = TaskState.FAILED


# class DownloadTask(QThread):
#     def __init__(
#         self,
#         task: DownloadTaskWidget,
#         _id: int,
#     ):
#         super(DownloadTask, self).__init__()
#         self._task = task
#         self._task_id = _id
#         self.lock = QMutex()
#         self._task.set_id(self._task_id)

#     def set_id(self, id):
#         self._task_id = id
#         self._task.set_id(id)

#     @property
#     def task(self):
#         return self._task

#     @property
#     def task_id(self):
#         return self._task_id

#     @property
#     def status(self):
#         return self._task.status

#     def run(self):
#         self._task.run()

#     def __eq__(self, another_task):
#         if isinstance(another_task, AnalyzeTask):
#             return self._task.task == another_task
#         elif isinstance(another_task, DownloadTaskWidget):
#             return self._task.task == another_task.task
#         else:
#             return (
#                 isinstance(another_task, DownloadTask)
#                 and self._task.task == another_task.task.task
#             )

# DownloadWidget.py (continued)
class DownloadTask(QObject):
    """
    Refactored DownloadTask with asyncio support
    """
    def __init__(
        self,
        task: DownloadTaskWidget,
        _id: int,
    ):
        super(DownloadTask, self).__init__()
        self._task = task
        self._task_id = _id
        self.lock = QMutex()
        self._task.set_id(self._task_id)
        self._event_loop = None

    def set_event_loop(self, loop):
        """
        Set the asyncio event loop for this task
        """
        self._event_loop = loop
        self._task.set_event_loop(loop)

    def set_id(self, id):
        self._task_id = id
        self._task.set_id(id)

    @property
    def task(self):
        return self._task

    @property
    def task_id(self):
        return self._task_id

    @property
    def status(self):
        return self._task.status

    async def start_async(self):
        """
        Async version of start method
        """
        if self._event_loop:
            # Run the async task in the event loop
            asyncio.run_coroutine_threadsafe(self._task.run_async(), self._event_loop)
        else:
            # Fallback to synchronous version if no event loop
            self.start()

    def start(self):
        """
        Synchronous version of start for backward compatibility
        """
        self._task.run()

    def __eq__(self, another_task):
        if isinstance(another_task, AnalyzeTask):
            return self._task.task == another_task
        elif isinstance(another_task, DownloadTaskWidget):
            return self._task.task == another_task.task
        else:
            return (
                isinstance(another_task, DownloadTask)
                and self._task.task == another_task.task.task
            )