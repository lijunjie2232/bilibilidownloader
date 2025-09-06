# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QWidget,
)


class Ui_SettingDialog(object):
    def setupUi(self, SettingDialog):
        if not SettingDialog.objectName():
            SettingDialog.setObjectName("SettingDialog")
        SettingDialog.resize(480, 390)
        SettingDialog.setStyleSheet("")
        self.groupBox = QGroupBox(SettingDialog)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 461, 81))
        self.groupBox.setStyleSheet(
            "QGroupBox {\n"
            "    border: 2px solid #dfe6e9;\n"
            "    border-radius: 5px;\n"
            "    margin-top: 10px;\n"
            "}\n"
            "QGroupBox::title {\n"
            "    top: -10px;\n"
            "    left: 5px;\n"
            "    padding: 2px;\n"
            "}"
        )
        self.ffmpeg_path_line = QLineEdit(self.groupBox)
        self.ffmpeg_path_line.setObjectName("ffmpeg_path_line")
        self.ffmpeg_path_line.setGeometry(QRect(110, 20, 321, 21))
        self.ffmpeg_path_btn = QToolButton(self.groupBox)
        self.ffmpeg_path_btn.setObjectName("ffmpeg_path_btn")
        self.ffmpeg_path_btn.setGeometry(QRect(430, 20, 21, 21))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 20, 91, 21))
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.ffmpeg_link_label = QLabel(self.groupBox)
        self.ffmpeg_link_label.setObjectName("ffmpeg_link_label")
        self.ffmpeg_link_label.setGeometry(QRect(110, 50, 201, 20))
        self.ffmpeg_link_label.setTextFormat(Qt.TextFormat.RichText)
        self.ffmpeg_link_label.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.ffmpeg_link_label.setOpenExternalLinks(True)
        self.groupBox_2 = QGroupBox(SettingDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 100, 461, 91))
        self.groupBox_2.setStyleSheet(
            "QGroupBox {\n"
            "    border: 2px solid #dfe6e9;\n"
            "    border-radius: 5px;\n"
            "    margin-top: 10px;\n"
            "}\n"
            "QGroupBox::title {\n"
            "    top: -10px;\n"
            "    left: 5px;\n"
            "    padding: 2px;\n"
            "}"
        )
        self.download_path_line = QLineEdit(self.groupBox_2)
        self.download_path_line.setObjectName("download_path_line")
        self.download_path_line.setGeometry(QRect(110, 20, 321, 21))
        self.download_path_btn = QToolButton(self.groupBox_2)
        self.download_path_btn.setObjectName("download_path_btn")
        self.download_path_btn.setGeometry(QRect(430, 20, 21, 21))
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(10, 20, 91, 21))
        self.label_2.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(240, 50, 101, 31))
        self.label_3.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.parallel_box = QSpinBox(self.groupBox_2)
        self.parallel_box.setObjectName("parallel_box")
        self.parallel_box.setGeometry(QRect(350, 50, 71, 31))
        self.parallel_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.parallel_box.setAccelerated(False)
        self.parallel_box.setCorrectionMode(
            QAbstractSpinBox.CorrectionMode.CorrectToNearestValue
        )
        self.parallel_box.setMinimum(1)
        self.parallel_box.setMaximum(12)
        self.auto_album_check = QCheckBox(self.groupBox_2)
        self.auto_album_check.setObjectName("auto_album_check")
        self.auto_album_check.setGeometry(QRect(170, 50, 20, 31))
        self.auto_album_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.auto_album_check.setStyleSheet(
            "QCheckBox {\n" "    text-align: left;\n" "}"
        )
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.label_4.setGeometry(QRect(10, 50, 151, 31))
        self.label_4.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.groupBox_3 = QGroupBox(SettingDialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 200, 461, 131))
        self.groupBox_3.setStyleSheet(
            "QGroupBox {\n"
            "    border: 2px solid #dfe6e9;\n"
            "    border-radius: 5px;\n"
            "    margin-top: 10px;\n"
            "}\n"
            "QGroupBox::title {\n"
            "    top: -10px;\n"
            "    left: 5px;\n"
            "    padding: 2px;\n"
            "}"
        )
        self.proxy_url_line = QLineEdit(self.groupBox_3)
        self.proxy_url_line.setObjectName("proxy_url_line")
        self.proxy_url_line.setGeometry(QRect(110, 60, 331, 21))
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(10, 60, 91, 21))
        self.label_5.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.proxy_enable_check = QCheckBox(self.groupBox_3)
        self.proxy_enable_check.setObjectName("proxy_enable_check")
        self.proxy_enable_check.setGeometry(QRect(170, 20, 20, 31))
        self.proxy_enable_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.proxy_enable_check.setStyleSheet(
            "QCheckBox {\n" "    text-align: left;\n" "}"
        )
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(10, 20, 151, 31))
        self.label_7.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName("label_8")
        self.label_8.setGeometry(QRect(240, 20, 101, 31))
        self.label_8.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.sys_proxy_check = QCheckBox(self.groupBox_3)
        self.sys_proxy_check.setObjectName("sys_proxy_check")
        self.sys_proxy_check.setGeometry(QRect(350, 20, 20, 31))
        self.sys_proxy_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.sys_proxy_check.setStyleSheet(
            "QCheckBox {\n" "    text-align: left;\n" "}"
        )
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName("label_9")
        self.label_9.setGeometry(QRect(10, 90, 151, 31))
        self.label_9.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.ssl_enable_check = QCheckBox(self.groupBox_3)
        self.ssl_enable_check.setObjectName("ssl_enable_check")
        self.ssl_enable_check.setGeometry(QRect(170, 90, 20, 31))
        self.ssl_enable_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.ssl_enable_check.setStyleSheet(
            "QCheckBox {\n" "    text-align: left;\n" "}"
        )
        self.ok_btn = QPushButton(SettingDialog)
        self.ok_btn.setObjectName("ok_btn")
        self.ok_btn.setGeometry(QRect(310, 350, 75, 31))
        self.cancel_btn = QPushButton(SettingDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setGeometry(QRect(390, 350, 75, 31))

        self.retranslateUi(SettingDialog)

        QMetaObject.connectSlotsByName(SettingDialog)

    # setupUi

    def retranslateUi(self, SettingDialog):
        SettingDialog.setWindowTitle(
            QCoreApplication.translate("SettingDialog", "Dialog", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("SettingDialog", "ffmpeg", None)
        )
        self.ffmpeg_path_line.setText("")
        self.ffmpeg_path_btn.setText(
            QCoreApplication.translate("SettingDialog", "...", None)
        )
        self.label.setText(
            QCoreApplication.translate("SettingDialog", "ffmpeg.exe path:", None)
        )
        self.ffmpeg_link_label.setText(
            QCoreApplication.translate(
                "SettingDialog",
                '<html><head/><body><p><a href="https://ffmpeg.org/download.html"><span style=" font-weight:700; text-decoration: underline; color:#5555ff;">visit offical download page</span></a> of ffmpeg</p></body></html>',
                None,
            )
        )
        self.groupBox_2.setTitle(
            QCoreApplication.translate("SettingDialog", "download", None)
        )
        self.download_path_btn.setText(
            QCoreApplication.translate("SettingDialog", "...", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("SettingDialog", "default directory:", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("SettingDialog", "parallel:", None)
        )
        self.auto_album_check.setText("")
        self.label_4.setText(
            QCoreApplication.translate(
                "SettingDialog", "auto create album directory:", None
            )
        )
        self.groupBox_3.setTitle(
            QCoreApplication.translate("SettingDialog", "network", None)
        )
        self.label_5.setText(
            QCoreApplication.translate("SettingDialog", "proxy url:", None)
        )
        self.proxy_enable_check.setText("")
        self.label_7.setText(
            QCoreApplication.translate("SettingDialog", "use proxy:", None)
        )
        self.label_8.setText(
            QCoreApplication.translate("SettingDialog", "use system proxy:", None)
        )
        self.sys_proxy_check.setText("")
        self.label_9.setText(
            QCoreApplication.translate("SettingDialog", "verify ssl:", None)
        )
        self.ssl_enable_check.setText("")
        self.ok_btn.setText(QCoreApplication.translate("SettingDialog", "Ok", None))
        self.cancel_btn.setText(
            QCoreApplication.translate("SettingDialog", "Cancel", None)
        )

    # retranslateUi
