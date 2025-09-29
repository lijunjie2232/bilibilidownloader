import math
from copy import deepcopy
from pathlib import Path
from shutil import move, rmtree
from traceback import print_exc, print_stack

import curl_cffi
import requests
from bilibilicore.api import DashStream
from bilibilicore.config import Config
from bilibilicore.utils import clean_tmp, combine
from loguru import logger
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
    copy_session,
    get_link,
    load_image_to_label,
    m4s_merger,
    sanitize_filename,
    thread,
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


@unique
class TaskOp(Enum):
    """Docstring for MyEnum."""

    CANCEL = -1
    PAUSE = 3
    RESUME = 2


# Add these imports at the top of the file
import asyncio

import aiohttp


class DownloadTaskWidget(QWidget, Ui_DownloadTask):
    _op_occured = Signal(TaskOp)  # 0: cancel, 1: pause, 2: resume
    _status_change_occurred = Signal(TaskState, TaskState)

    def __init__(
        self,
        analyze_task: AnalyzeTask,
        save_dir: str,
        id: int,
    ):
        super(DownloadTaskWidget, self).__init__()
        self.setupUi(self)

        self._analyze_task = analyze_task
        self._save_dir = Path(save_dir)
        self._vname = self._analyze_task.vname
        self._title = self._analyze_task.title
        self._quality_str = self._analyze_task.quality_str
        self._duration_str = self._analyze_task.duration_str
        self._id = id
        self._alid = self._analyze_task.alid

        self._video: DashStream = self._analyze_task.selected_video
        self._audio: DashStream = self._analyze_task.selected_audio
        self._filename = self.filename_gen()

        if self._vname and Config().download.auto_create_album_dir:
            self._save_dir /= sanitize_filename(self._vname)
        self._save_dir.mkdir(parents=True, exist_ok=True)

        self._status = TaskState.PENDING
        self._status_mutex = QRecursiveMutex()
        self._op_mutex = QMutex()
        self._condition = QWaitCondition()
        self._download_task = DownloadTask(
            self._analyze_task,
            self._filename,
            self._save_dir,
            self._id,
            self,
        )
        """
        _task_result_occurred
        _task_info_occurred
        _task_error_occurred
        _progress_bar_update_occured
        
        _on_task_error
        _on_task_finished
        _on_task_info
        """
        connect_component(
            self._download_task,
            "_task_result_occurred",
            self._on_task_finished,
        )
        connect_component(
            self._download_task,
            "_task_info_occurred",
            self._on_task_info,
        )
        connect_component(
            self._download_task,
            "_task_error_occurred",
            self._on_task_error,
        )
        connect_component(
            self._download_task,
            "_progress_bar_update_occured",
            self.update_progress,
        )

        self.resume_icon = None
        self.pause_icon = None
        self.cancel_icon = None
        self.icon_init()

        # 初始化控件
        self.id_label.setText(str(id) if id > -1 else "")
        self.title_label.setText(self._title)
        self.vname_label.setText(self._vname)
        self.quality_label.setText(self._quality_str)
        self.duration_label.setText(self._duration_str)
        self.progress_bar.setValue(0)
        connect_component(
            self.cancel_btn,
            "clicked",
            self.cancel,
        )
        connect_component(
            self.pause_btn,
            "clicked",
            self.pause,
        )
        connect_component(
            self.resume_btn,
            "clicked",
            self.resume,
        )

        # connect_component(
        #     self.debug_btn,
        #     "clicked",
        #     self.debug_handler,
        # )
        self.debug_btn.setVisible(False)

        # 设置缩略图
        if self._analyze_task.img or self._analyze_task.pic_url:
            load_image_to_label(
                self.thumbnail_label,
                url=self._analyze_task.pic_url,
                img=self._analyze_task.img,
            )
        else:
            self.thumbnail_label.setText("No Image")
    
    @property
    def bytes_update_occurred(self):
        return self._download_task.bytes_update_occurred

    def filename_gen(self):
        width = math.ceil(math.log10(self._analyze_task.total))

        # 使用 f-string 补零
        padded_id = str(self._alid).rjust(width, "0")

        return sanitize_filename(f"{padded_id}_{self._analyze_task.title}")

    def debug_handler(self):
        pass

    @property
    def id(self):
        return self._id

    @property
    def task(self):
        return self._download_task

    @property
    def analyze_task(self):
        return self._analyze_task

    def __eq__(self, value):
        if isinstance(value, DownloadTaskWidget):
            return self._analyze_task == value.analyze_task
        elif isinstance(value, AnalyzeTask):
            return self._analyze_task == value
        elif isinstance(value, DownloadTask):
            return self._analyze_task == value.task

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
        self.resume_btn.setIcon(self.resume_icon)
        self.resume_btn.setIconSize(_ICON_SIZE)
        self.pause_btn.setIcon(self.pause_icon)
        self.pause_btn.setIconSize(_ICON_SIZE)

    @property
    def status(self):
        with QMutexLocker(self._status_mutex):
            return self._status

    @property
    def status_mutex(self):
        return self._status_mutex

    @property
    def op_mutex(self):
        return self._op_mutex

    def set_status(self, status: TaskState, emit=True):
        with QMutexLocker(self._status_mutex):
            original_status = self._status
            self._status = status
            if emit:
                self._status_change_occurred.emit(original_status, status)

    def resume(
        self,
    ):
        with QMutexLocker(self._op_mutex):
            # self.resume_btn.setVisible(False)
            # self.pause_btn.setVisible(True)
            # self._op_occured.emit(TaskOp.RESUME)
            # # self._condition.wakeAll()
            # self._download_task.resume()
            self._op_occured.emit(TaskOp.RESUME)

    def pause(
        self,
    ):
        with QMutexLocker(self._op_mutex):
            # self.resume_btn.setVisible(True)
            # self.pause_btn.setVisible(False)
            # self._op_occured.emit(TaskOp.PAUSE)
            # self._download_task.pause()
            self._op_occured.emit(TaskOp.PAUSE)

    def cancel(
        self,
    ):
        with QMutexLocker(self._op_mutex):
            # self._op_occured.emit(TaskOp.CANCEL)
            # self._download_task.cancel()
            self._op_occured.emit(TaskOp.CANCEL)

    def update_progress(
        self,
        downloaded: int,
        total: int,
    ):
        if not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
        self.progress_bar.setValue(downloaded)
        if self.progress_bar.maximum() != total:
            self.progress_bar.setMaximum(total)

    def update_status_label(self, text):
        self.status_label.setText(text)

    def _on_task_error(
        self,
        exception: Exception,
    ):
        logger.error(f"Task {self._id} error: {exception}")
        self.set_status(TaskState.FAILED)

    def _on_task_finished(self, result: bool):
        with QMutexLocker(self._status_mutex):
            if result:
                self.set_status(TaskState.FINISHED)
            else:
                if self.status == TaskState.RUNNING:
                    self.set_status(TaskState.FAILED)

    def _on_task_info(self, info, err=""):
        self.update_status_label(info)
        if err:
            logger.error(err)


class DownloadTask(QThread):
    __CONFIG__ = Config()
    __SESSION__ = copy_session(__CONFIG__.session)

    _task_result_occurred = Signal(bool)
    _task_info_occurred = Signal(str, str)
    _task_error_occurred = Signal(Exception)

    _progress_bar_update_occured = Signal(int, int)  # 用于更新进度条
    _task_bytes_update_occurred = Signal(int)

    def __init__(
        self,
        task: AnalyzeTask,
        filename,
        save_dir,
        id,
        parent=None,
    ):
        super().__init__(parent)

        self._task = task
        self._download_task = None
        self._loop = None
        self._save_dir = Path(save_dir)
        # if self._task.vname and Config().download.auto_create_album_dir:
        #     self._save_dir /= self._task.vname
        self._save_dir.mkdir(parents=True, exist_ok=True)
        self._id = id
        self._filename = filename

        self._video: DashStream = self._task.selected_video
        self._audio: DashStream = self._task.selected_audio

        # self._status = TaskState.PENDING
        # self._status_mutex = QMutex()
        # self._status_mutex = QRecursiveMutex()
        # self._condition = QWaitCondition()
        self._event_loop = None

        # net component
        self.client = None
    
    @property
    def bytes_update_occurred(self):
        return self._task_bytes_update_occurred

    def task_refetch(self):
        logger.info(f"do task info refetch, task: {self._task}")
        self._task.init_detail()
        self._task.vq_apply()
        self._task.aq_apply()
        self._video: DashStream = self._task.selected_video
        self._audio: DashStream = self._task.selected_audio

    def _init_download(self):

        self.client = curl_cffi.AsyncSession(
            headers=dict(self.session.headers),
            cookies=dict(self.session.cookies),
            verify=Config().network.ssl_verify,
            max_clients=256,
            trust_env=False,
            allow_redirects=True,
            impersonate="chrome",
            http_version="v3",
            loop=self._loop,
        )

    @property
    def task(self):
        return self._task

    @property
    def session(self) -> requests.Session:
        return self.__SESSION__

    def set_id(self, id):
        self._id = id
        self.id_label.setText(str(id + 1))

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
            if isinstance(backup_url, str):  # pragma: no cover
                backup_url = [backup_url]
            elif isinstance(backup_url, list):  # pragma: no cover
                backup_url = url_list.extend(backup_url)

        for attempt, current_url in enumerate(url_list, start=1):

            try:
                file_size = output_path.stat().st_size if output_path.exists() else 0
                mode = "ab"

                url, _, total_size, _, continual_download, _, headers = get_link(
                    current_url,
                    dict(self.session.headers),
                    start=file_size,
                    cookies=dict(self.session.cookies),
                    # proxy=proxy, # TODO
                )
                if not continual_download:
                    output_path.unlink()
                    file_size = 0
                    mode = "wb"
                if file_size == total_size:
                    move(output_path, final_file_path)
                    return True
                downloaded_size = file_size
                self._progress_bar_update_occured.emit(downloaded_size, total_size)

                with open(output_path, mode) as f:
                    async with self.client.stream(
                        url=url,
                        headers=headers,
                        cookies=self.session.cookies,
                        timeout=30,
                        method="GET",
                    ) as res:
                        res.raise_for_status()
                        async for chunk in res.aiter_content():
                            if not chunk:
                                break
                            chunk_size = len(chunk)
                            f.write(chunk)
                            downloaded_size += chunk_size
                            self._progress_bar_update_occured.emit(
                                downloaded_size,
                                total_size,
                            )
                            self._task_bytes_update_occurred.emit(chunk_size)

                move(output_path, final_file_path)
                return True  # 成功下载

            except Exception as e:
                print_exc()
                if attempt < len(url_list):
                    continue  # 尝试备用链接
                else:
                    logger.warning(f"无法下载 {desc}：{e}", level="error")
                    return e

    async def async_download(self):
        """
        Async version of run method
        """
        try:
            self._task_info_occurred.emit("正在分析...", "")

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
                self._task_result_occurred.emit(True)
                self._progress_bar_update_occured.emit(1, 1)
                self._task_info_occurred.emit("下载完成", "")
                return True
            tmp_out_path = self._save_dir / f"{out_path.stem}_tmp{out_path.suffix}"

            self._task_info_occurred.emit("正在下载视频", "")

            result = await self.async_download_file(
                url=video.base_url,
                backup_url=video.backup_url,
                output_path=tmp_video_path,
                desc="video",
            )
            logger.debug(result)
            assert result is True, result
            # self._task_info_occurred.emit("下载视频失败或取消", repr(result))

            # elif audio:
            self._task_info_occurred.emit("正在下载音频", "")
            result = await self.async_download_file(
                url=audio.base_url,
                backup_url=audio.backup_url,
                output_path=tmp_audio_path,
                desc="audio",
            )
            assert result is True, result
            # if result is not True:
            # self._task_info_occurred.emit("下载音频失败或取消", repr(result))
            # else:
            self._task_info_occurred.emit("正在合并文件", "")
            self._progress_bar_update_occured.emit(0, 0)
            # combine(
            #     v=tmp_video_path,
            #     a=tmp_audio_path,
            #     out_file=tmp_out_path,
            #     fmt=None if self._task.fmt != ori_vfmt else None,
            #     overwrite=True,
            # )
            m4s_merger(
                tmp_video_path,
                tmp_audio_path,
                tmp_out_path,
            )
            move(tmp_out_path, out_path)

            self._task_info_occurred.emit("缓存清理", "")
            clean_tmp(
                tmp_video_path,
                tmp_audio_path,
            )
            self._task_result_occurred.emit(True)
            self._progress_bar_update_occured.emit(1, 1)
            self._task_info_occurred.emit("下载完成", "")
            return result
        except Exception as e:
            print_exc()
            print_stack()
            self._task_error_occurred.emit(e)
            self._task_info_occurred.emit("下载失败", repr(e))
            self._task_result_occurred.emit(False)
            return False

    async def do_download(self, retry=3):
        while retry:
            retry -= 1
            try:
                result = await self.async_download()
                logger.debug(result)
                assert result
            except Exception as e:
                self.task_refetch()
                logger.error(e)
                print_exc()
            finally:
                self._download_task = None

    def stop(self):
        try:
            if not self.is_running:
                return
            if self._download_task:
                self._download_task.cancel()
            if self.client:
                self.client.stop()
        except Exception as e:
            print_exc()
            self._task_error_occurred.emit(e)
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    def run(self, loop=None):
        if self.is_running:
            return
        self._loop = loop or asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._init_download()

        try:
            self._loop.run_until_complete(self.do_download())
        except asyncio.CancelledError as e:
            logger.warning(e)
            self._task_error_occurred.emit(e)
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()
            self._loop = None

    def pause(self):
        try:
            self.stop()
        except Exception as e:
            print_exc()
            self._task_error_occurred.emit(e)

    def resume(self):
        try:
            self.task_refetch()
            self.run()
        except Exception as e:
            print_exc()
            self._task_error_occurred.emit(e)

    def cancel(self):
        try:
            self.stop()
        except Exception as e:
            print_exc()
            self._task_error_occurred.emit(e)

    @property
    def is_running(self):
        try:
            if self._loop is not asyncio.get_running_loop():
                return False
            else:
                return self._loop.is_closed()
        except Exception:
            return False
