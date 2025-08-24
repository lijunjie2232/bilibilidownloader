from functools import partial
from pathlib import Path
from time import sleep
from traceback import print_exc

from bilibilicore.api import DashStream, Season, Stream, Video
from bilibilicore.config import Config
from PySide6.QtCore import (
    QFile,
    QIODevice,
    QMutex,
    QMutexLocker,
    QObject,
    QRecursiveMutex,
    Qt,
    QThread,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QToolButton,
    QWidget,
)

from bilibilidownloader.ui import __MODULE_PATH__, Ui_Analyzer, Ui_AnalyzerTask
from bilibilidownloader.utils import (
    connect_component,
    get_aq,
    get_codec,
    get_vq,
    load_image_to_label,
    sec_to_str,
    set_menu,
    thread,
    url_check,
    url_equal,
)

_OUT_FMT = [
    "mp4",
    # "mkv",
    # "flv",
]


class DownloadCommit:
    def __init__(
        self,
        task_list,
        out_path,
    ):
        self._task_list = task_list
        self._out_path = out_path

    @property
    def task_list(self):
        return self._task_list

    @property
    def out_path(self):
        return self._out_path


class AnalyzerWidget(QDialog, Ui_Analyzer):
    _download_commit_occurred = Signal(DownloadCommit)

    def __init__(
        self,
        url,
        btype="video",
        title="Analyzer",
    ):
        super(AnalyzerWidget, self).__init__()
        # self.ui = Ui_Analyzer()
        # self.ui.setupUi(self)
        self.setupUi(self)

        self._url = url
        self._btype = btype
        self._fmt = "mp4"
        self._analyzer_list = []
        self._video_url_list = []
        self._analyzer: VideoAnalyzer = None
        self._task_list: list[AnalyzeTask] = []
        self._vq_filter = lambda _: True
        self._aq_filter = lambda _: True
        self._codec_filter = lambda _: True
        self._out_path = Config().download.default_path
        if self._out_path:
            self.path_line.setText(self._out_path)
        self._current_checked = 0
        self._total_checked = 0
        self.analyzer_init()
        self.setWindowTitle(title)
        connect_component(
            self.path_btn,
            "clicked",
            self.select_folder,
        )
        connect_component(
            self.url_btn,
            "clicked",
            self.task_fetch,
        )
        connect_component(
            self.select_all_btn,
            "clicked",
            self.select_all_task,
        )
        connect_component(
            self.select_no_btn,
            "clicked",
            self.select_no_task,
        )
        connect_component(
            self.select_reverse_btn,
            "clicked",
            self.select_reverse_task,
        )
        set_menu(
            self.fmt_select,
            _OUT_FMT,
            self.set_fmt,
            set_first=True,
        )
        self.info_fetch_progress_mutex = QMutex()
        connect_component(
            self.apply_filter_btn,
            "clicked",
            self.apply_filter,
        )
        connect_component(
            self.download_btn,
            "clicked",
            self.commit_download,
        )
        pass

    def commit_download(self):
        if not self._out_path:
            self.select_folder()
        if not self._out_path:
            self.alart("请选择下载目录")
            return
        download_commit = DownloadCommit(
            list(
                filter(
                    lambda task: task.checked,
                    self._task_list,
                )
            ),
            self._out_path,
        )
        if download_commit:
            self._download_commit_occurred.emit(download_commit)
            self.accept()
        self.reject()

    def apply_filter(self):
        for task in self._task_list:
            task.vq_apply(
                self._vq_filter,
                self._codec_filter,
            )
            task.aq_apply(self._aq_filter)
            task.set_fmt(self._fmt)

    def select_all_task(self):
        for item in self._task_list:
            item.check()

    def select_no_task(self):
        for item in self._task_list:
            item.uncheck()

    def select_reverse_task(self):
        for item in self._task_list:
            item.reverse_check()

    def task_fetch(self):

        self.info_fetch_bar.setMaximum(len(self._task_list))
        self.info_fetch_bar.setValue(0)
        self.info_fetch_bar.setVisible(True)
        for item in self._task_list:
            item.fetch()
        pass

    def set_fmt(
        self,
        fmt,
        idx=None,
        checked=False,
    ):
        self._fmt = fmt
        self.fmt_select.setText(fmt)

    def do_analyze(self):
        pass

    # @thread
    def analyzer_init(self):
        try:
            self.video_list = []
            self._analyzer_list = []
            if self._btype == "video":
                self.video_list = [self._url]
            elif self._btype == "collection":
                raise NotImplementedError()
            for url in self.video_list:
                analyzer = VideoAnalyzer(
                    url,
                )
                self._analyzer_list.append(analyzer)
            set_menu(
                self.url_btn,
                self.video_list,
                self.set_analyzer,
                set_first=True,
            )

        except Exception as e:
            raise e
            self.alart(str(e), "error")
            self.close()

    def _videos_occurred_handler(self, analyzer, videos):
        self.setVideoList(analyzer, videos)

    def _inited_occurred_handler(self, inited):
        if inited:
            self.analyzer_init_bar.setVisible(False)
            self.analyzer_init_bar.setMaximum(1)
            self.url_btn.setEnabled(True)
        else:
            self.url_btn.setEnabled(False)
            self.analyzer_init_bar.setMaximum(0)
            self.analyzer_init_bar.setVisible(True)

    def set_analyzer(
        self,
        _url,
        _idx,
        checked=False,
    ):
        self.url_btn.setText(str(_url))
        self._analyzer = self._analyzer_list[_idx]

        if self._analyzer.is_inited:
            return
        self._inited_occurred_handler(False)
        connect_component(
            self._analyzer,
            "_inited_occurred",
            self._inited_occurred_handler,
        )
        connect_component(
            self._analyzer,
            "_videos_occurred",
            self._videos_occurred_handler,
        )
        connect_component(
            self._analyzer,
            "_error_occurred",
            self.alart,
        )
        # self._analyzer._inited_occurred.connect(self._inited_occurred_handler)
        # self._analyzer._videos_occurred.connect(self._videos_occurred_handler)
        # partial(self.set_progress, bar=self.analyzer_init_bar)
        # self._analyzer._error_occurred.connect(self.alart)
        self._analyzer.task_init()
        self.setWindowTitle(self._analyzer.title)

    def set_progress(self, bar, value, total):
        bar.setMaximum(total)
        bar.setValue(value)

    def setVideoList(self, analyzer, task_list):
        # clear video_list
        self.video_part_list.clear()
        self._task_list = []
        for t in task_list:
            task = AnalyzeTask(**t)
            connect_component(
                task,
                "_info_fetch",
                self.info_fetch_handler,
            )
            connect_component(
                task,
                "_check_action_occurred",
                self.check_action_occurred_handler,
            )
            self._task_list.append(task)

            item = QListWidgetItem()
            item.setSizeHint(task.size())
            self.video_part_list.addItem(item)

            # 创建自定义控件
            self.video_part_list.setItemWidget(item, task)

        analyzer.set_tasks(self._task_list)

        fetched = sum(1 for t in self._task_list if t.info_fetched)
        checked = sum(1 for t in self._task_list if t.checked)
        self.set_total_count(len(self._task_list))
        self.info_fetch_bar.setValue(fetched)
        self.set_fetch_count(fetched)
        self._current_checked = 0
        self.update_current_select_count(checked)

        self.info_fetch_bar.setVisible(False)
        self.info_fetch_bar.setMaximum(len(self._task_list))
        pass

    def update_current_select_count(self, update=1):
        self._current_checked += update
        self.current_select_count_label.setText("current: %d" % self._current_checked)

    def update_total_select_count(self, update=1):
        self._total_checked += update
        self.total_select_count_label.setText("total: %d" % self._total_checked)

    def set_total_count(self, count):
        self.total_count_label.setText("total: %d" % count)

    def set_fetch_count(self, count):
        self.fetch_count_label.setText("fetch: %d" % count)

    def refresh_select_btns(self):
        vq_set = set()
        aq_set = set()
        codec_set = set()
        for task in self._task_list:
            vq_set.update(v["quality"].upper() for v in task.videos)
            codec_set.update(v["codec"].upper() for v in task.videos)
            aq_set.update(a["quality"].upper() for a in task.audios)
        set_menu(
            self.max_video,
            vq_set,
            self.set_vq,
            set_first=False,
        )
        set_menu(
            self.max_audio,
            aq_set,
            self.set_aq,
            set_first=False,
        )
        set_menu(
            self.codec_select,
            codec_set,
            self.set_codec,
            set_first=False,
        )

    def set_vq(self, vq, idx, checked):
        self.max_video.setText(vq)
        self._vq_filter = lambda v, q=vq: v[1].get("quality").upper() == q

    def set_aq(self, aq, idx, checked):
        self.max_audio.setText(aq)
        self._aq_filter = lambda a, q=aq: a[1].get("quality").upper() == q

    def set_codec(self, codec, idx, checked):
        self.codec_select.setText(codec)
        self._codec_filter = lambda v, c=codec: v[1].get("codec").upper() == c

    # @thread
    def info_fetch_handler(self, info_fetched):
        if info_fetched:
            with QMutexLocker(self.info_fetch_progress_mutex):
                self.info_fetch_bar.setValue(
                    self.info_fetch_bar.value() + 1,
                )
                self.set_fetch_count(self.info_fetch_bar.value())
        if self.info_fetch_bar.value() >= self.info_fetch_bar.maximum():
            self.info_fetch_bar.setVisible(False)
            self.refresh_select_btns()

    def check_action_occurred_handler(self, checked):
        # print(checked)
        self.update_current_select_count(1 if checked else -1)
        self.update_total_select_count(1 if checked else -1)

    def alart(
        self,
        message="alart",
        level="warning",
        close=False,
    ):
        assert level in ["warning", "error", "info"]
        msg_box = QMessageBox()

        if level == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
        else:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Info")

        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        if close:
            # hide self
            self.hide()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        path = Path(folder_path)

        if folder_path and not path.is_file():
            self.path_line.setText(path.__str__())
            self._out_path = path

    def progress_toast(
        self,
        message="alart",
        progress_bar=None,
    ):
        toast_dialog = QDialog()
        toast_dialog.setWindowTitle(message)

        if progress_bar:
            # set the progress bar to the dialog
            toast_dialog.setLayout(progress_bar)

        toast_dialog.show()

    @property
    def url(self):
        return self._url

    def __eq__(self, value):
        return type(self) is type(value) and url_equal(
            self._url,
            value.url,
        )


class VideoAnalyzer(QThread):
    _error_occurred = Signal(str, str)
    _warning_occurred = Signal(str, str)
    _progress_occurred = Signal(int, int)
    _videos_occurred = Signal(QObject, list)
    _inited_occurred = Signal(bool)
    _fetching_occurred = Signal(bool)

    def __init__(
        self,
        url,
        # btype="video",
    ):
        super().__init__()
        self._url = url.strip()
        # self._btype = btype
        self._aid = None
        self._cid = None
        self._bvid = None
        self._vname = None
        self._core = Season()
        self._inited = False
        self._fetched = False
        self._fetched_mutex = QMutex()
        self._task_list: list = []
        self._data = None
        self.bilibili_url_parser(self._url)

    # def set_task_list(self, task_list):
    #     self._task_list = task_list

    @property
    def title(self):
        return self._vname or self._bvid or self._aid

    # @thread
    def bilibili_url_parser(self, url):
        if url.isdigit():
            assert len(url) == 15, self._error_occurred.emit(
                "expect length of aid is 15",
                "error",
            )
            self._aid = url
            return
        elif url.startswith("http"):
            parsed_url = url_check(url)
            assert parsed_url
            path_segments = parsed_url.path.strip("/").split("/")
            url = path_segments[1]
        assert url.startswith("BV1") and len(url) == 12, self._error_occurred.emit(
            "expect length of bvid is 12 and startswith BV1",
            "error",
        )
        self._bvid = url

    @property
    def is_inited(self):
        return self._inited

    @property
    def is_fetched(self):
        return self._fetched

    @thread
    def task_init(self):
        if self._inited:
            return
        result = None
        if self._bvid:
            result = self._core.get_view(self._bvid)
        elif self._aid != None:
            result = self._core.get_view(self._aid)
        else:
            self._error_occurred.emit(
                "no bvid or aid",
                "error",
            )
        if result and result.get("code", -1) == 0:
            self._data = result["data"]
            _aid = result["data"]["aid"]
            _bvid = result["data"]["bvid"]
            self._vname = video_name = result["data"]["title"]
            videos = result["data"]["pages"]
            total = len(videos)
            # task_list = []
            # # for video in videos:
            # for video in videos[:7]:
            #     task = {
            #         "aid": _aid,
            #         "bid": _bvid,
            #         "cid": video["cid"],
            #         "name": video["part"],
            #         "video_name": video_name,
            #         "page": video["page"],
            #         "pic_url": video["first_frame"],
            #         "duration": video["duration"],
            #     }
            #     task_list.append(task)
            task_list = [
                {
                    "aid": _aid,
                    "bid": _bvid,
                    "cid": video["cid"],
                    "alid": idx,
                    "name": video["part"],
                    "video_name": video_name,
                    "page": video["page"],
                    "total": total,
                    "pic_url": video["first_frame"],
                    "duration": video["duration"],
                }
                for idx, video in enumerate(videos, 1)
            ]
            self._inited = True
            self._videos_occurred.emit(self, task_list)
            self._inited_occurred.emit(self._inited)
        else:
            self._error_occurred.emit(
                f"{result['code']}: {result['msg']}",
                "error",
            )

    def set_tasks(self, task_list):
        self._task_list = task_list


class AnalyzeTask(
    QWidget,
    Ui_AnalyzerTask,
):
    _info_fetch = Signal(bool)
    _menu_handler = Signal(object, object, object)
    _check_action_occurred = Signal(bool)
    """
    {
        "cid": 25735926609,
        "page": 1,
        "from": "vupload",
        "part": "私有大模型部署和调参：AI大模型开发是干什么的？",
        "duration": 271,
        "vid": "",
        "weblink": "",
        "dimension": {"width": 2560, "height": 1440, "rotate": 0},
        "first_frame": "http://i0.hdslb.com/bfs/storyff/n241222sa2x73twl0cz4ay1c13n8g8m5_firsti.jpg",
        "ctime": 0,
    }
    """

    def __init__(
        self,
        aid,
        bid,
        cid,
        alid,
        name,
        video_name,
        page,
        total,
        pic_url,
        duration,
        fnval=16,
    ):
        super(AnalyzeTask, self).__init__()
        # self.ui = Ui_AnalyzerTask()
        # self.ui.setupUi(self)
        self.setupUi(self)

        self._aid = aid
        self._bid = bid
        self._cid = cid
        self._alid = alid
        self._title = name
        self._vname = video_name
        self._id = page
        self._pic_url = pic_url
        self._duration = duration
        self._fnval = fnval
        self._total = total

        # core
        self._core = Video()

        # video data
        self._thumbnail_img: QImage = None
        self._data = {}
        self._videos = []
        self._audios = []
        self._vq_filter = lambda _: True
        self._aq_filter = lambda _: True
        self._codec_filter = lambda _: True
        self._selected_vid = 0
        self._selected_aid = 0
        self._fmt = "mp4"

        # status
        self.inited = False
        self.fetching = False
        self.fetch_mutex = QMutex()
        self.info_fetched = False
        self.checked = False
        self.downloaded = False
        self.init_components()

        self._check_lock = QMutex()
        connect_component(self.info_fetch_btn, "clicked", self.fetch)

        # signal
        self._menu_handler.connect(self.handle_menu)

    @property
    def title(self):
        return self._title

    @property
    def vname(self):
        return self._vname

    @property
    def id(self):
        return self._id

    @property
    def alid(self):
        return self._alid

    @property
    def total(self):
        return self._total

    @property
    def fmt(self):
        return self._fmt

    @property
    def selected_video(self):
        return self._videos[self._selected_vid] if self._videos else None

    @property
    def selected_audio(self):
        return self._audios[self._selected_aid] if self._audios else None

    @property
    def duration_str(self):
        return sec_to_str(self._duration)

    @property
    def quality_str(self):
        return (
            f'{self.selected_video.get("quality","")}'
            + f'/{self.selected_video["codec"]} '
            + f'{self.selected_audio.get("quality", "?")}'
        )

    @property
    def img(self):
        return self._thumbnail_img

    @img.setter
    def img(self, img):
        self._thumbnail_img = img

    @property
    def pic_url(self):
        return self._pic_url

    def vq_apply(self, vq_filter=None, codec_filter=None):
        self._vq_filter = vq_filter or self._vq_filter
        self._codec_filter = codec_filter or self._codec_filter
        vq_videos = list(
            filter(
                self._vq_filter,
                enumerate(self.videos),
            )
        )
        if len(vq_videos) == 0:
            return
        codec_videos = list(
            filter(
                self._codec_filter,
                vq_videos,
            )
        )
        if len(codec_videos) > 0:
            vq_videos = codec_videos
        if len(vq_videos):
            self._selected_vid = vq_videos[0][0]
            self.video_select.setText(
                f'{vq_videos[0][1]["quality"]}/{vq_videos[0][1]["codec"]}',
            )
        else:
            self._selected_vid = 0
            self.video_select.setText(
                f'{self.video[0]["quality"]}/{self.videos[0]["codec"]}',
            )

    def aq_apply(self, _filter=None):
        self._aq_filter = _filter or self._aq_filter
        aq_videos = list(
            filter(
                self._aq_filter,
                enumerate(self._audios),
            )
        )
        if aq_videos:
            self._selected_aid = aq_videos[0][0]
            self.audio_select.setText(
                f'{aq_videos[0][1]["quality"]}',
            )
        else:
            self._selected_aid = 0
            self.audio_select.setText(
                f'{self.audios[0]["quality"]}',
            )

    def handle_menu(self, *args):
        # print(f"handle_menu: {QThread.currentThread()}")
        set_menu(*args)

    @property
    def videos(self):
        return self._videos

    @property
    def audios(self):
        return self._audios

    @thread
    def fetch(self):
        try:
            if self.fetching:
                return
            if self.fetching:
                return
            with QMutexLocker(self.fetch_mutex):
                if self.fetching:
                    return
                self.fetching = True
                # self.init_components()
            # print(f"fetch: {QThread.currentThread()}")
            self.init_detail()
            with QMutexLocker(self.fetch_mutex):
                self.fetching = False
            sleep(1)
        except Exception as e:
            print_exc()
            raise e
        finally:
            with QMutexLocker(self.fetch_mutex):
                self.fetching = False

    def show_error(self, msg):
        self.progress_bar.setVisible(False)
        self.error_label.setText(msg)
        self.error_label.setVisible(True)

    @thread
    def init_components(self):

        self.video_select.setEnabled(self.inited)
        self.audio_select.setEnabled(self.inited)
        self.fmt_select.setEnabled(self.inited)
        self.select_check.setEnabled(self.inited)
        self.progress_bar.setVisible(not self.inited)
        self.error_label.setVisible(False)

        connect_component(
            self.select_check,
            "clicked",
            self.select_checked_handler,
        )

        if not self.inited:
            self.id_label.setText(str(self._id))
            self.title_label.setText(self._title)
            self.vname_label.setText(self._vname)
            self.time_label.setText(sec_to_str(self._duration))
            self.inited = True

    def init_detail(self):
        # print(f"init_detail: {QThread.currentThread()}")
        self.error_label.setVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(True)

        load_image_to_label(
            self.thumbnail_label, self._pic_url, callback=partial(setattr, self, "img")
        )
        result = self._core.get_playurl(self._aid, self._cid, self._fnval)
        assert result["code"] == 0, result["message"]
        data = result["data"]
        self._data = data
        assert self._fnval == 16, NotImplementedError()
        # media = data["dash"] if self._fnval == 16 else data["durl"]
        media = data["dash"]
        self._videos = []
        self._audios = []
        for idx, video in enumerate(media["video"]):
            vq = get_vq(video["id"])
            codec = get_codec(video["codecid"])
            if not vq or not codec:
                continue
            self._videos.append(
                {
                    "id": idx,
                    "quality": vq,
                    "url": video["baseUrl"],
                    "codecs": video["codecs"],
                    "codecid": video["codecid"],
                    "codec": codec,
                    "frame_rate": video["frameRate"],
                    "stream": DashStream(**video),
                }
            )

        for idx, audio in enumerate(media["audio"]):
            aq = get_aq(audio["id"])
            if not aq:
                continue
            self._audios.append(
                {
                    "id": idx,
                    "quality": aq,
                    "url": audio["baseUrl"],
                    "codecs": audio["codecs"],
                    "stream": DashStream(**audio),
                }
            )

        self._menu_handler.emit(
            self.video_select,
            [f'{item["quality"]}/{item["codec"]}' for item in self._videos],
            self.set_video,
        )
        self._menu_handler.emit(
            self.audio_select,
            [item["quality"] for item in self._audios],
            self.set_audio,
        )

        self._menu_handler.emit(
            self.fmt_select,
            _OUT_FMT,
            self.set_fmt,
        )

        self.progress_bar.setMaximum(1)
        self.init_components()

        self.info_fetched = True
        self._info_fetch.emit(self.info_fetched)

    def set_video(self, text, id, checked):
        self.video_select.setText(text)
        self._selected_vid = id

    def set_audio(self, text, id, checked):
        self.audio_select.setText(text)
        self._selected_aid = id

    def set_fmt(self, fmt, id=0, checked=False):
        self.fmt_select.setText(fmt)
        self._fmt = fmt

    @property
    def id(self):
        return id

    @thread
    def check(self):
        if self.checked or not self.select_check.isEnabled:
            return
        with QMutexLocker(self._check_lock):
            if self.checked:
                return
            self.checked = True
            self.select_check.setChecked(True)
            self._check_action_occurred.emit(self.checked)

    @thread
    def uncheck(self):
        if not self.checked or not self.select_check.isEnabled:
            return
        with QMutexLocker(self._check_lock):
            if not self.checked:
                return
            self.checked = False
            self.select_check.setChecked(False)
            self._check_action_occurred.emit(self.checked)

    @thread
    def reverse_check(self):
        if not self.select_check.isEnabled:
            return
        with QMutexLocker(self._check_lock):
            if self.checked:
                self.checked = False
                self.select_check.setChecked(False)
            else:
                self.checked = True
                self.select_check.setChecked(True)
            self._check_action_occurred.emit(self.checked)

    @thread
    def select_checked_handler(self):
        with QMutexLocker(self._check_lock):
            self.checked = self.select_check.isChecked()
            self._check_action_occurred.emit(self.checked)

    def __eq__(self, another_task):
        if isinstance(another_task, AnalyzeTask):
            if self is another_task:
                return True
            else:
                return another_task._aid == self._aid and another_task._cid == self._cid
        else:
            return False
