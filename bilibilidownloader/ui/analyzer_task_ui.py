# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer_task.ui'
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
    QCheckBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class Ui_AnalyzerTask(object):
    def setupUi(self, AnalyzerTask):
        if not AnalyzerTask.objectName():
            AnalyzerTask.setObjectName("AnalyzerTask")
        AnalyzerTask.setEnabled(True)
        AnalyzerTask.resize(990, 120)
        self.thumbnail_label = QLabel(AnalyzerTask)
        self.thumbnail_label.setObjectName("thumbnail_label")
        self.thumbnail_label.setEnabled(True)
        self.thumbnail_label.setGeometry(QRect(64, 2, 116, 116))
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.id_label = QLabel(AnalyzerTask)
        self.id_label.setObjectName("id_label")
        self.id_label.setEnabled(True)
        self.id_label.setGeometry(QRect(2, 2, 60, 116))
        self.id_label.setAlignment(Qt.AlignCenter)
        self.audio_text = QLabel(AnalyzerTask)
        self.audio_text.setObjectName("audio_text")
        self.audio_text.setEnabled(True)
        self.audio_text.setGeometry(QRect(510, 80, 40, 32))
        self.audio_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.audio_select = QToolButton(AnalyzerTask)
        self.audio_select.setObjectName("audio_select")
        self.audio_select.setEnabled(True)
        self.audio_select.setGeometry(QRect(550, 80, 161, 32))
        self.audio_select.setPopupMode(QToolButton.MenuButtonPopup)
        self.video_text = QLabel(AnalyzerTask)
        self.video_text.setObjectName("video_text")
        self.video_text.setEnabled(True)
        self.video_text.setGeometry(QRect(300, 80, 40, 32))
        self.video_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.video_select = QToolButton(AnalyzerTask)
        self.video_select.setObjectName("video_select")
        self.video_select.setEnabled(True)
        self.video_select.setGeometry(QRect(340, 80, 161, 32))
        self.video_select.setPopupMode(QToolButton.MenuButtonPopup)
        self.select_check = QCheckBox(AnalyzerTask)
        self.select_check.setObjectName("select_check")
        self.select_check.setEnabled(True)
        self.select_check.setGeometry(QRect(930, 0, 60, 120))
        self.select_check.setLayoutDirection(Qt.LeftToRight)
        self.select_check.setStyleSheet(
            "QCheckBox::indicator{\n"
            "	width: 60px;\n"
            "	height : 116px;\n"
            "}\n"
            "QCheckBox::hover{\n"
            "background-color: #bbdefb;\n"
            "}"
        )
        self.select_check.setIconSize(QSize(60, 120))
        self.select_check.setChecked(False)
        self.select_check.setAutoExclusive(False)
        self.select_check.setTristate(False)
        self.vname_label = QLabel(AnalyzerTask)
        self.vname_label.setObjectName("vname_label")
        self.vname_label.setEnabled(True)
        self.vname_label.setGeometry(QRect(200, 30, 600, 20))
        font = QFont()
        font.setPointSize(10)
        font.setItalic(True)
        self.vname_label.setFont(font)
        self.title_label = QLabel(AnalyzerTask)
        self.title_label.setObjectName("title_label")
        self.title_label.setEnabled(True)
        self.title_label.setGeometry(QRect(200, 10, 600, 20))
        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(True)
        self.title_label.setFont(font1)
        self.fmt_text = QLabel(AnalyzerTask)
        self.fmt_text.setObjectName("fmt_text")
        self.fmt_text.setEnabled(True)
        self.fmt_text.setGeometry(QRect(720, 80, 40, 32))
        self.fmt_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.fmt_select = QToolButton(AnalyzerTask)
        self.fmt_select.setObjectName("fmt_select")
        self.fmt_select.setEnabled(True)
        self.fmt_select.setGeometry(QRect(760, 80, 161, 32))
        self.fmt_select.setPopupMode(QToolButton.MenuButtonPopup)
        self.progress_bar = QProgressBar(AnalyzerTask)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setEnabled(True)
        self.progress_bar.setGeometry(QRect(200, 65, 720, 5))
        self.progress_bar.setStyleSheet(
            "\n"
            "QProgressBar {\n"
            "    border: 0px solid #fd79a8;\n"
            "    border-radius: 5px;\n"
            "    background-color: #fdfdfd;\n"
            "}\n"
            "\n"
            "QProgressBar::chunk {\n"
            "    background-color: qlineargradient(\n"
            "        x1: 0, y1: 0,\n"
            "        x2: 1, y2: 0,\n"
            "        stop: 0 #fce4ec,\n"
            "        stop: 1 #fd79a8\n"
            "    );\n"
            "    border-radius: 10px;\n"
            "}"
        )
        self.progress_bar.setMaximum(0)
        self.progress_bar.setValue(-1)
        self.time_text = QLabel(AnalyzerTask)
        self.time_text.setObjectName("time_text")
        self.time_text.setEnabled(True)
        self.time_text.setGeometry(QRect(205, 80, 35, 32))
        self.time_text.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.time_label = QLabel(AnalyzerTask)
        self.time_label.setObjectName("time_label")
        self.time_label.setEnabled(True)
        self.time_label.setGeometry(QRect(240, 80, 51, 32))
        self.time_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.error_label = QLabel(AnalyzerTask)
        self.error_label.setObjectName("error_label")
        self.error_label.setGeometry(QRect(200, 55, 721, 21))
        font2 = QFont()
        font2.setPointSize(9)
        font2.setBold(True)
        font2.setItalic(True)
        font2.setUnderline(True)
        font2.setStrikeOut(False)
        self.error_label.setFont(font2)
        self.error_label.setLayoutDirection(Qt.LeftToRight)
        self.error_label.setStyleSheet("QLabel{\n" "	color: #d63031;\n" "}")
        self.info_fetch_btn = QPushButton(AnalyzerTask)
        self.info_fetch_btn.setObjectName("info_fetch_btn")
        self.info_fetch_btn.setGeometry(QRect(810, 10, 101, 31))

        self.retranslateUi(AnalyzerTask)

        QMetaObject.connectSlotsByName(AnalyzerTask)

    # setupUi

    def retranslateUi(self, AnalyzerTask):
        AnalyzerTask.setWindowTitle(
            QCoreApplication.translate("AnalyzerTask", "Form", None)
        )
        self.thumbnail_label.setText(
            QCoreApplication.translate("AnalyzerTask", "Loading ...", None)
        )
        self.id_label.setText(QCoreApplication.translate("AnalyzerTask", "1000", None))
        self.audio_text.setText(
            QCoreApplication.translate("AnalyzerTask", "\u97f3\u8d28\uff1a", None)
        )
        self.audio_select.setText(
            QCoreApplication.translate("AnalyzerTask", "loading ...", None)
        )
        self.video_text.setText(
            QCoreApplication.translate("AnalyzerTask", "\u753b\u8d28\uff1a", None)
        )
        self.video_select.setText(
            QCoreApplication.translate("AnalyzerTask", "loading ...", None)
        )
        self.select_check.setText("")
        self.vname_label.setText(
            QCoreApplication.translate("AnalyzerTask", "Video Name", None)
        )
        self.title_label.setText(
            QCoreApplication.translate("AnalyzerTask", "Video Name", None)
        )
        self.fmt_text.setText(
            QCoreApplication.translate("AnalyzerTask", "\u683c\u5f0f\uff1a", None)
        )
        self.fmt_select.setText(
            QCoreApplication.translate("AnalyzerTask", "loading ...", None)
        )
        self.time_text.setText(
            QCoreApplication.translate("AnalyzerTask", "\u65f6\u957f\uff1a", None)
        )
        self.time_label.setText(
            QCoreApplication.translate("AnalyzerTask", "1:10:51", None)
        )
        self.error_label.setText("")
        self.info_fetch_btn.setText(
            QCoreApplication.translate("AnalyzerTask", "Info Re-Fetch", None)
        )

    # retranslateUi
