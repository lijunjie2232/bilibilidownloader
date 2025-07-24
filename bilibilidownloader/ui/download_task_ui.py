# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'download_task.ui'
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
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QWidget,
)

import icon_rc


class Ui_DownloadTask(object):
    def setupUi(self, DownloadTask):
        if not DownloadTask.objectName():
            DownloadTask.setObjectName("DownloadTask")
        DownloadTask.resize(593, 72)
        self.progress_bar = QProgressBar(DownloadTask)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setGeometry(QRect(130, 50, 420, 16))
        self.progress_bar.setStyleSheet(
            "QProgressBar {\n"
            "    background-color: #dfe6e9;\n"
            "    border: 0px solid #fce4ec;\n"
            "    border-radius: 5px;\n"
            "}\n"
            "\n"
            "QProgressBar::chunk {\n"
            "    background-color: qlineargradient(x1: 0, y1: 0,\n"
            "            x2: 1, y2: 0,\n"
            "            stop: 0 #fce4ec,\n"
            "            stop: 1 #fd79a8);\n"
            "    border-radius: 5px;\n"
            "}"
        )
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setInvertedAppearance(False)
        self.title_label = QLabel(DownloadTask)
        self.title_label.setObjectName("title_label")
        self.title_label.setGeometry(QRect(129, 2, 291, 20))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.title_label.setFont(font)
        self.quality_label = QLabel(DownloadTask)
        self.quality_label.setObjectName("quality_label")
        self.quality_label.setGeometry(QRect(420, 2, 130, 20))
        self.quality_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.thumbnail_label = QLabel(DownloadTask)
        self.thumbnail_label.setObjectName("thumbnail_label")
        self.thumbnail_label.setGeometry(QRect(50, 2, 68, 68))
        self.thumbnail_label.setAutoFillBackground(True)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pause_or_resume_btn = QPushButton(DownloadTask)
        self.pause_or_resume_btn.setObjectName("pause_or_resume_btn")
        self.pause_or_resume_btn.setEnabled(True)
        self.pause_or_resume_btn.setGeometry(QRect(562, 8, 24, 24))
        icon = QIcon()
        icon.addFile(
            ":/icon/bilibilidownloader/ui/assert/pause.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pause_or_resume_btn.setIcon(icon)
        self.pause_or_resume_btn.setIconSize(QSize(24, 16))
        self.cancel_btn = QPushButton(DownloadTask)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setGeometry(QRect(562, 40, 24, 24))
        icon1 = QIcon()
        icon1.addFile(
            ":/icon/bilibilidownloader/ui/assert/cancel.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.cancel_btn.setIcon(icon1)
        self.id_label = QLabel(DownloadTask)
        self.id_label.setObjectName("id_label")
        self.id_label.setGeometry(QRect(0, 2, 48, 60))
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vname_label = QLabel(DownloadTask)
        self.vname_label.setObjectName("vname_label")
        self.vname_label.setGeometry(QRect(129, 24, 291, 20))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setItalic(True)
        self.vname_label.setFont(font1)
        self.duration_label = QLabel(DownloadTask)
        self.duration_label.setObjectName("duration_label")
        self.duration_label.setGeometry(QRect(420, 24, 130, 20))
        self.duration_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_label = QLabel(DownloadTask)
        self.status_label.setObjectName("status_label")
        self.status_label.setGeometry(QRect(130, 50, 420, 16))
        self.status_label.setFont(font1)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.debug_btn = QPushButton(DownloadTask)
        self.debug_btn.setObjectName("debug_btn")
        self.debug_btn.setEnabled(True)
        self.debug_btn.setGeometry(QRect(420, 10, 24, 24))
        self.debug_btn.setIcon(icon)
        self.debug_btn.setIconSize(QSize(24, 16))

        self.retranslateUi(DownloadTask)

        QMetaObject.connectSlotsByName(DownloadTask)

    # setupUi

    def retranslateUi(self, DownloadTask):
        DownloadTask.setWindowTitle(
            QCoreApplication.translate("DownloadTask", "Form", None)
        )
        self.title_label.setText(
            QCoreApplication.translate("DownloadTask", "Video Name", None)
        )
        self.quality_label.setText(
            QCoreApplication.translate("DownloadTask", "1080P", None)
        )
        self.thumbnail_label.setText(
            QCoreApplication.translate("DownloadTask", "No Pic", None)
        )
        self.pause_or_resume_btn.setText("")
        self.cancel_btn.setText("")
        self.id_label.setText(QCoreApplication.translate("DownloadTask", "1000", None))
        self.vname_label.setText(
            QCoreApplication.translate("DownloadTask", "Video Name", None)
        )
        self.duration_label.setText(
            QCoreApplication.translate("DownloadTask", "1080P", None)
        )
        self.status_label.setText(
            QCoreApplication.translate("DownloadTask", "pending", None)
        )
        self.debug_btn.setText("")

    # retranslateUi
