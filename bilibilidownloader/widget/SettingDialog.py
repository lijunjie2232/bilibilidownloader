from functools import partial
from pathlib import Path

from bilibilicore.config import Config
from loguru import logger
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QFileDialog

from bilibilidownloader.ui import Ui_SettingDialog
from bilibilidownloader.utils import connect_component


class SettingDialog(QDialog, Ui_SettingDialog):

    def __init__(
        self,
        parent=None,
    ):
        super(SettingDialog, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowIcon(
            QIcon(
                ":/icon/bilibilidownloader/ui/assert/settings.svg",
            ),
        )

        self.setting = Config()

        self.init_components()

    def init_components(self):
        """
        Initialize UI components with values from config file
        """

        config = self.setting

        # FFmpeg settings
        self.ffmpeg_path_line.setText(config.ffmpeg.path)

        # Download settings
        self.download_path_line.setText(config.download.path)
        self.parallel_box.setValue(config.download.parallel)
        self.auto_album_check.setChecked(config.download.auto_create_album_dir)

        # Proxy settings
        self.proxy_enable_check.setChecked(config.network.use_proxy)
        self.sys_proxy_check.setChecked(
            config.network.sys_proxy
        )  # Note: 'custom' seems to control system proxy usage
        self.proxy_url_line.setText(config.network.proxy_url)

        if not self.proxy_enable_check.isChecked():
            self.sys_proxy_check.setEnabled(False)
            self.proxy_url_line.setEnabled(False)
        elif self.sys_proxy_check.isChecked():
            self.proxy_url_line.setEnabled(False)

        # SSL settings
        self.ssl_enable_check.setChecked(config.network.ssl_verify)

        connect_component(
            self.ffmpeg_path_btn,
            "clicked",
            partial(self.select_file, self.ffmpeg_path_line),
        )
        connect_component(
            self.download_path_btn,
            "clicked",
            partial(self.select_folder, self.download_path_line),
        )
        # Connect the proxy enable checkbox to the handler
        connect_component(
            self.proxy_enable_check,
            "stateChanged",
            self.on_proxy_enable_changed,
        )
        connect_component(
            self.sys_proxy_check,
            "stateChanged",
            self.on_sys_proxy_changed,
        )

        # connect ok and cancel button
        connect_component(
            self.ok_btn,
            "clicked",
            self.accept,
        )
        connect_component(
            self.cancel_btn,
            "clicked",
            self.reject,
        )

    def on_proxy_enable_changed(self, state):
        """
        Handle proxy enable checkbox state changes.
        Enable/disable sys_proxy_check and proxy_url_line based on proxy_enable_check state.

        Args:
            state: The check state (Qt.Checked or Qt.Unchecked)
        """
        # Convert state to boolean (Qt.Checked = 2, Qt.Unchecked = 0)
        is_enabled = state == 2  # Qt.Checked

        # Enable/disable dependent widgets
        self.sys_proxy_check.setEnabled(is_enabled)
        self.proxy_url_line.setEnabled(is_enabled)

    def on_sys_proxy_changed(self, state):
        """
        Handle proxy enable checkbox state changes.
        Enable/disable sys_proxy_check and proxy_url_line based on proxy_enable_check state.

        Args:
            state: The check state (Qt.Checked or Qt.Unchecked)
        """
        # Convert state to boolean (Qt.Checked = 2, Qt.Unchecked = 0)
        is_enabled = state != 2  # Qt.Checked

        # Enable/disable dependent widgets
        self.proxy_url_line.setEnabled(is_enabled)

    def select_folder(self, line=None):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        path = Path(folder_path)

        if folder_path and not path.is_file():
            line.setText(path.__str__())

    def select_file(self, line=None):
        file_path = QFileDialog.getOpenFileName(self, "Select File")
        path = Path(file_path)
        if file_path and not path.is_file():
            line.setText(path.__str__())

    def save_settings(self):
        """
        Save settings to config file
        """

        config = self.setting

        # FFmpeg settings
        config.set("ffmpeg.path", self.ffmpeg_path_line.text())

        # Download settings
        config.set("download.path", self.download_path_line.text())
        config.set("download.parallel", self.parallel_box.value())
        config.set("download.auto_create_album_dir", self.auto_album_check.isChecked())

        # Proxy settings
        config.set("network.use_proxy", self.proxy_enable_check.isChecked())
        config.set("network.sys_proxy", self.sys_proxy_check.isChecked())
        config.set("network.proxy_url", self.proxy_url_line.text())

        # SSL settings
        config.set("network.ssl_verify", self.ssl_enable_check.isChecked())

        config._save_config_on_exit()

    def accept(self):
        self.save_settings()
        return super().accept()

    def reject(self):
        return super().reject()
