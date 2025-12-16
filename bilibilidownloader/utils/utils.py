import re
import threading
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import partial
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from weakref import ref

from bilibilicore.config import Config
from niquests import Session
from PySide6.QtConcurrent import QtConcurrent
from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QRunnable,
    Qt,
    QThread,
    QThreadPool,
    QUrl,
    QWaitCondition,
    Signal,
)
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtWidgets import QFileDialog, QLabel, QMenu

# QThreadPool.globalInstance().setMaxThreadCount(3)


def normalize_url(url):
    parsed = urlparse(url)
    # Remove query parameters and trailing slash
    normalized = parsed._replace(query=None, path=parsed.path.rstrip("/"))
    return urlunparse(normalized)


def url_equal(url1, url2):
    return normalize_url(url1) == normalize_url(url2)


def url_check(url):
    try:
        result = urlparse(url)
        return result
    except:
        return False


# _network_manager = None
# _LOCK = threading.Lock()

# def get_network_manager():
#     global _network_manager
#     if not _network_manager:
#         with _LOCK:
#             if not _network_manager:
#                 from PySide6.QtNetwork import QNetworkAccessManager
#                 _network_manager = QNetworkAccessManager()
#     return _network_manager


# def thread(my_func):
#     def wrapper(*args, **kwargs):
#         my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
#         my_thread.start()
#         return my_thread
#     return wrapper


def thread(my_func):
    class Runnable(QRunnable):
        def __init__(self, func, *args, **kwargs):
            super().__init__()
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.callback = kwargs.pop("callback", None)

        def run(self):
            if self.callback:
                self.callback(self.func(*self.args, **self.kwargs))
            else:
                self.func(*self.args, **self.kwargs)

    def wrapper(*args, **kwargs):
        runnable = Runnable(my_func, *args, **kwargs)
        QThreadPool.globalInstance().start(runnable)
        return runnable

    return wrapper


@thread
def load_image_to_label(
    label: QLabel,
    url: str = None,
    img: QImage = None,
) -> QImage:
    assert url or img
    if not img:
        res = Config().session.get(url)
        img = QImage.fromData(res.content)
    pixmap = QPixmap.fromImage(img)
    scaled_pixmap = pixmap.scaled(
        label.size(),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    label.setScaledContents(False)
    label.setPixmap(scaled_pixmap)
    return img


def sec_to_str(seconds: int):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"


def ui_wired(base_class, ui_class):
    def wrapper(cls):
        # 设置继承关系
        cls.__bases__ = (base_class, ui_class)

        # 重写 __init__ 方法
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            super(cls, self).__init__()
            self.setupUi(self)
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper


def set_menu(
    tool_btn,
    menu_items,
    trigger_func,
    set_first=True,
):
    menu = QMenu(tool_btn)

    # Create actions (menu items)
    for idx, fmt in enumerate(menu_items):
        action = QAction(fmt, tool_btn)
        action.triggered.connect(
            lambda _checked, _fmt=fmt, _idx=idx: trigger_func(_fmt, _idx, _checked)
        )
        menu.addAction(action)
        if idx == 0 and set_first:
            trigger_func(fmt, idx, False)
    tool_btn.setMenu(menu)


def connect_component(
    component,
    action,
    callback,
    except_callback=None,
    reconnect=True,
):

    try:
        if action:
            signal = getattr(component, action)
            if reconnect and hasattr(signal, "disconnect"):
                signal.disconnect()
        elif reconnect and hasattr(component, "disconnect"):
            component.disconnect()
    except:
        pass
    try:
        if action:
            signal = getattr(component, action)
            if hasattr(signal, "connect"):
                signal.connect(callback)
        elif hasattr(component, "connect"):
            component.connect(callback)
    except Exception as e:
        if except_callback:
            except_callback(e)


def copy_session(session: Session):
    new_session = Session()
    new_session.cookies.update(deepcopy(session.cookies))
    new_session.headers.update(deepcopy(session.headers))

    return new_session


def sanitize_filename(filename, replacement="_"):
    """
    Replace invalid characters with underscore for cross-platform compatibility
    """
    # Replace forbidden characters with underscore
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, filename)
    return sanitized


if __name__ == "__main__":
    print(sec_to_str(9999))
    print(sec_to_str(1000))
    print(sec_to_str(675))
    print(sec_to_str(489))
