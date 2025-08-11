import sys
from io import BytesIO
from time import sleep

import qrcode
from bilibilicore.api import Passport, User
from bilibilicore.config import Config
from PySide6.QtCore import QFile, QIODevice, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QImage, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QScrollArea,
    QToolButton,
)
from tqdm import tqdm

from bilibilidownloader.ui import __MODULE_PATH__, Ui_MainWindow
from bilibilidownloader.utils import (
    connect_component,
    load_image_to_label,
    set_menu,
    thread,
    url_check,
)
from bilibilidownloader.widget import (
    AnalyzerWidget,
    DownloadCommit,
    DownloadTask,
    DownloadTaskWidget,
    LoginDialog,
    TaskManager,
    TaskState,
)

# from bilibilidownloader.utils import ui_wired


class MainWindow(
    QMainWindow,
    Ui_MainWindow,
):

    def __init__(self):
        super(MainWindow, self).__init__()
        # self = Ui_MainWindow()
        self.setupUi(self)

        self.analyze_type = "video"
        self._task_manager = TaskManager(Config().download.parallel)
        self._task_count = 0

        self.link_type_selector_init(self.link_type_selector)

        self.analyzer = None
        self.statusbar_count_label = QLabel()

        self.user = None
        self.user_init()
        connect_component(
            self.login_op,
            "triggered",
            self.login_op_triggered,
        )
        self.status_bar_init()
        self.show()

    def status_bar_init(self):
        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(":/icon/bilibilidownloader/ui/assert/pending.svg"),
        )
        icon_label.setFixedSize(
            self.statusbar.height(),
            self.statusbar.height(),
        )
        self.statusbar.addPermanentWidget(icon_label)
        self.statusbar_count_label.setText("done: 0 / total: 0")
        self.statusbar.addPermanentWidget(self.statusbar_count_label)

    def login_op_triggered(self):
        if self.user is not None:
            print("login" if self.user is None else f"logout({self.name_label.text()})")
            self.user = None
            self.name_label.setText("未登录")
            self.head_label.setPixmap(QPixmap(""))
            self.login_op.setText("login")
        else:
            login_dialog = LoginDialog()
            connect_component(
                login_dialog,
                "_qr_login_finished",
                self._handle_qr_login_finished,
            )
            connect_component(
                login_dialog,
                "finished",
                login_dialog.closeDialog,
            )
            login_dialog.show()

    def _handle_qr_login_finished(self, succeed):
        if succeed:
            self.user_init()

    def user_init(self):
        user = User()
        result = user.nav_me()
        if result["code"] != 0:
            self.user = None
            load_image_to_label(
                self.head_label,
                "http://i0.hdslb.com/bfs/face/member/noface.jpg",
            )
            self.name_label.setText(result["message"])
            self.alart("Please login first")
        else:
            self.user = user
            load_image_to_label(
                self.head_label,
                result["data"]["face"],
            )
            self.name_label.setText(result["data"]["uname"])
        self.login_op.setText(
            "login" if self.user is None else f"logout({self.name_label.text()})"
        )

    def alart(
        self,
        message="alart",
        level="warning",
        confirm=False,
    ):
        assert level in ["warning", "error", "info"]
        msg_box = QMessageBox()

        if level == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
        elif level == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
        else:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Info")

        msg_box.setText(message)
        if confirm:
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
        else:
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        response = msg_box.exec()

        if confirm:
            return response == QMessageBox.StandardButton.Yes
        return True

    def add_task(self, task: DownloadTaskWidget):
        # 创建 QListWidgetItem
        item = QListWidgetItem()
        item.setSizeHint(task.size())
        self.download_list.addItem(item)

        # 创建自定义控件
        self.download_list.setItemWidget(item, task)

    def link_type_selector_init(self, button):
        if not button:
            return

        set_menu(
            button,
            [
                "video",
                "collection",
            ],
            self.on_dropdown_action,
            set_first=True,
        )

        button.clicked.disconnect()
        button.clicked.connect(
            self.on_link_type_selector_clicked,
        )

    def on_link_type_selector_clicked(self):
        analyzer = AnalyzerWidget(
            # "https://www.bilibili.com/video/BV1utM7zqE32",
            self.link_line.text(),
            btype=self.analyze_type,
        )

        if analyzer != self.analyzer:
            if self.analyzer is not None:
                del self.analyzer
            analyzer.setAttribute(
                Qt.WidgetAttribute.WA_DeleteOnClose,
                False,
            )
            analyzer.rejected.connect(analyzer.hide)
            analyzer._download_commit_occurred.connect(self.commit_download)
            self.analyzer = analyzer
        else:
            # analyzer is show -> alart
            self.alart(
                message="same url",
                level="warning",
            )
        if not self.analyzer.isVisible():
            self.analyzer.show()
        pass

    def on_dropdown_action(
        self,
        option,
        idx=0,
        checked=False,
    ):
        self.link_type_selector.setText(option)
        self.analyze_type = option

    def commit_download(self, commit: DownloadCommit):
        task_list = commit.task_list
        out_path = commit.out_path

        for t in task_list:
            self.add_download_task(
                t,
                out_path,
            )

    def add_download_task(
        self,
        t,
        out_path,
    ):
        task = DownloadTaskWidget(
            t,
            out_path,
            self.download_list.count(),
        )
        result = self._task_manager.add_task(task)
        if result:
            self._task_count += result
            self.add_task(task)
        else:
            del task

    def cancel_task_handler(self, task:DownloadTaskWidget):
        task_widget = self.download_list.item(task.id)
        if task_widget and task_widget.status == TaskState.CANCELED:
            # 移除该项
            self.download_list.takeItem(task.id)
            for id in range(self.download_list.count()):
                self.download_list.item(id).set_id(id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
