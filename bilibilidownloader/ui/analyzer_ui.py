# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'analyzer.ui'
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
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)


class Ui_Analyzer(object):
    def setupUi(self, Analyzer):
        if not Analyzer.objectName():
            Analyzer.setObjectName("Analyzer")
        Analyzer.resize(1024, 768)
        self.video_part_list = QListWidget(Analyzer)
        self.video_part_list.setObjectName("video_part_list")
        self.video_part_list.setGeometry(QRect(2, 52, 1020, 668))
        self.video_part_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.video_part_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.max_video = QToolButton(Analyzer)
        self.max_video.setObjectName("max_video")
        self.max_video.setGeometry(QRect(690, 10, 80, 32))
        self.max_video.setPopupMode(QToolButton.MenuButtonPopup)
        self.vq_label = QLabel(Analyzer)
        self.vq_label.setObjectName("vq_label")
        self.vq_label.setGeometry(QRect(630, 10, 60, 32))
        self.vq_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.aq_text = QLabel(Analyzer)
        self.aq_text.setObjectName("aq_text")
        self.aq_text.setGeometry(QRect(780, 10, 60, 32))
        self.aq_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.max_audio = QToolButton(Analyzer)
        self.max_audio.setObjectName("max_audio")
        self.max_audio.setGeometry(QRect(840, 10, 80, 32))
        self.max_audio.setPopupMode(QToolButton.MenuButtonPopup)
        self.apply_filter_btn = QPushButton(Analyzer)
        self.apply_filter_btn.setObjectName("apply_filter_btn")
        self.apply_filter_btn.setGeometry(QRect(930, 10, 84, 32))
        self.download_cancle = QPushButton(Analyzer)
        self.download_cancle.setObjectName("download_cancle")
        self.download_cancle.setGeometry(QRect(938, 730, 84, 32))
        self.select_all_btn = QPushButton(Analyzer)
        self.select_all_btn.setObjectName("select_all_btn")
        self.select_all_btn.setGeometry(QRect(10, 730, 84, 32))
        self.select_reverse_btn = QPushButton(Analyzer)
        self.select_reverse_btn.setObjectName("select_reverse_btn")
        self.select_reverse_btn.setGeometry(QRect(100, 730, 84, 32))
        self.select_no_btn = QPushButton(Analyzer)
        self.select_no_btn.setObjectName("select_no_btn")
        self.select_no_btn.setGeometry(QRect(190, 730, 84, 32))
        self.download_btn = QToolButton(Analyzer)
        self.download_btn.setObjectName("download_btn")
        self.download_btn.setGeometry(QRect(850, 730, 84, 32))
        self.download_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self.path_line = QLineEdit(Analyzer)
        self.path_line.setObjectName("path_line")
        self.path_line.setGeometry(QRect(400, 730, 411, 32))
        self.path_btn = QToolButton(Analyzer)
        self.path_btn.setObjectName("path_btn")
        self.path_btn.setGeometry(QRect(810, 730, 32, 32))
        self.info_fetch_bar = QProgressBar(Analyzer)
        self.info_fetch_bar.setObjectName("info_fetch_bar")
        self.info_fetch_bar.setGeometry(QRect(2, 720, 1020, 3))
        self.info_fetch_bar.setStyleSheet(
            "QProgressBar{text-align:center;background-color:#dfe6e9;}\n"
            "QProgressBar::chunk{background-color:#fd79a8;}"
        )
        self.info_fetch_bar.setMaximum(0)
        self.info_fetch_bar.setValue(-1)
        self.info_fetch_bar.setTextVisible(False)
        self.fmt_select = QToolButton(Analyzer)
        self.fmt_select.setObjectName("fmt_select")
        self.fmt_select.setGeometry(QRect(390, 10, 80, 32))
        self.fmt_select.setPopupMode(QToolButton.MenuButtonPopup)
        self.fmt_text = QLabel(Analyzer)
        self.fmt_text.setObjectName("fmt_text")
        self.fmt_text.setGeometry(QRect(330, 10, 60, 32))
        self.fmt_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.url_btn = QToolButton(Analyzer)
        self.url_btn.setObjectName("url_btn")
        self.url_btn.setGeometry(QRect(10, 10, 221, 32))
        self.url_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self.analyzer_init_bar = QProgressBar(Analyzer)
        self.analyzer_init_bar.setObjectName("analyzer_init_bar")
        self.analyzer_init_bar.setEnabled(True)
        self.analyzer_init_bar.setGeometry(QRect(12, 41, 216, 3))
        self.analyzer_init_bar.setStyleSheet(
            "QProgressBar{text-align:center;background-color:#dfe6e9;}\n"
            "QProgressBar::chunk{background-color:#fd79a8;}"
        )
        self.analyzer_init_bar.setMaximum(0)
        self.analyzer_init_bar.setValue(-1)
        self.analyzer_init_bar.setTextVisible(False)
        self.codec_text = QLabel(Analyzer)
        self.codec_text.setObjectName("codec_text")
        self.codec_text.setGeometry(QRect(480, 10, 60, 32))
        self.codec_text.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.codec_select = QToolButton(Analyzer)
        self.codec_select.setObjectName("codec_select")
        self.codec_select.setGeometry(QRect(540, 10, 80, 32))
        self.codec_select.setPopupMode(QToolButton.MenuButtonPopup)
        self.current_select_count_label = QLabel(Analyzer)
        self.current_select_count_label.setObjectName("current_select_count_label")
        self.current_select_count_label.setGeometry(QRect(280, 730, 108, 16))
        self.current_select_count_label.setAlignment(Qt.AlignCenter)
        self.total_count_label = QLabel(Analyzer)
        self.total_count_label.setObjectName("total_count_label")
        self.total_count_label.setGeometry(QRect(240, 10, 81, 16))
        self.total_count_label.setAlignment(Qt.AlignCenter)
        self.fetch_count_label = QLabel(Analyzer)
        self.fetch_count_label.setObjectName("fetch_count_label")
        self.fetch_count_label.setGeometry(QRect(240, 24, 81, 16))
        self.fetch_count_label.setAlignment(Qt.AlignCenter)
        self.total_select_count_label = QLabel(Analyzer)
        self.total_select_count_label.setObjectName("total_select_count_label")
        self.total_select_count_label.setGeometry(QRect(280, 744, 108, 16))
        self.total_select_count_label.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Analyzer)

        QMetaObject.connectSlotsByName(Analyzer)

    # setupUi

    def retranslateUi(self, Analyzer):
        Analyzer.setWindowTitle(QCoreApplication.translate("Analyzer", "Dialog", None))
        self.max_video.setText(QCoreApplication.translate("Analyzer", "1080P", None))
        self.vq_label.setText(
            QCoreApplication.translate(
                "Analyzer", "\u6700\u9ad8\u753b\u8d28\uff1a", None
            )
        )
        self.aq_text.setText(
            QCoreApplication.translate(
                "Analyzer", "\u6700\u9ad8\u97f3\u8d28\uff1a", None
            )
        )
        self.max_audio.setText(QCoreApplication.translate("Analyzer", "132K", None))
        self.apply_filter_btn.setText(
            QCoreApplication.translate(
                "Analyzer", "\u5e94\u7528\u5230\u5168\u90e8", None
            )
        )
        self.download_cancle.setText(
            QCoreApplication.translate("Analyzer", "\u53d6\u6d88", None)
        )
        self.select_all_btn.setText(
            QCoreApplication.translate("Analyzer", "\u5168\u9009", None)
        )
        self.select_reverse_btn.setText(
            QCoreApplication.translate("Analyzer", "\u53cd\u9009", None)
        )
        self.select_no_btn.setText(
            QCoreApplication.translate("Analyzer", "\u5168\u4e0d\u9009", None)
        )
        self.download_btn.setText(
            QCoreApplication.translate(
                "Analyzer", "\u4e0b\u8f7d\u9009\u4e2d\u9879", None
            )
        )
        self.path_btn.setText(QCoreApplication.translate("Analyzer", "...", None))
        self.fmt_select.setText(QCoreApplication.translate("Analyzer", "MP4", None))
        self.fmt_text.setText(
            QCoreApplication.translate(
                "Analyzer", "\u8f93\u51fa\u683c\u5f0f\uff1a", None
            )
        )
        self.url_btn.setText(
            QCoreApplication.translate("Analyzer", "113696558814120", None)
        )
        self.codec_text.setText(
            QCoreApplication.translate(
                "Analyzer", "\u8f93\u5165\u7f16\u7801\uff1a", None
            )
        )
        self.codec_select.setText(QCoreApplication.translate("Analyzer", "AVC", None))
        self.current_select_count_label.setText(
            QCoreApplication.translate("Analyzer", "current: 0", None)
        )
        self.total_count_label.setText(
            QCoreApplication.translate("Analyzer", "total: 0", None)
        )
        self.fetch_count_label.setText(
            QCoreApplication.translate("Analyzer", "fetch: 0", None)
        )
        self.total_select_count_label.setText(
            QCoreApplication.translate("Analyzer", "total: 0", None)
        )

    # retranslateUi
