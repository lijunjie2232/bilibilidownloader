# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'setting_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QDialog,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpinBox, QToolButton, QWidget)

class Ui_SettingDialog(object):
    def setupUi(self, SettingDialog):
        if not SettingDialog.objectName():
            SettingDialog.setObjectName(u"SettingDialog")
        SettingDialog.resize(480, 360)
        SettingDialog.setStyleSheet(u"")
        self.groupBox = QGroupBox(SettingDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 10, 461, 61))
        self.groupBox.setStyleSheet(u"QGroupBox {\n"
"    border: 2px solid #dfe6e9;\n"
"    border-radius: 5px;\n"
"    margin-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    top: -10px;\n"
"    left: 5px;\n"
"    padding: 2px;\n"
"}")
        self.ffmpeg_path_line = QLineEdit(self.groupBox)
        self.ffmpeg_path_line.setObjectName(u"ffmpeg_path_line")
        self.ffmpeg_path_line.setGeometry(QRect(110, 20, 321, 21))
        self.ffmpeg_path_btn = QToolButton(self.groupBox)
        self.ffmpeg_path_btn.setObjectName(u"ffmpeg_path_btn")
        self.ffmpeg_path_btn.setGeometry(QRect(430, 20, 21, 21))
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 91, 21))
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.groupBox_2 = QGroupBox(SettingDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 80, 461, 91))
        self.groupBox_2.setStyleSheet(u"QGroupBox {\n"
"    border: 2px solid #dfe6e9;\n"
"    border-radius: 5px;\n"
"    margin-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    top: -10px;\n"
"    left: 5px;\n"
"    padding: 2px;\n"
"}")
        self.download_path_line = QLineEdit(self.groupBox_2)
        self.download_path_line.setObjectName(u"download_path_line")
        self.download_path_line.setGeometry(QRect(110, 20, 321, 21))
        self.download_path_btn = QToolButton(self.groupBox_2)
        self.download_path_btn.setObjectName(u"download_path_btn")
        self.download_path_btn.setGeometry(QRect(430, 20, 21, 21))
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 20, 91, 21))
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(240, 50, 101, 31))
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.parallel_box = QSpinBox(self.groupBox_2)
        self.parallel_box.setObjectName(u"parallel_box")
        self.parallel_box.setGeometry(QRect(350, 50, 71, 31))
        self.parallel_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.parallel_box.setAccelerated(False)
        self.parallel_box.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.parallel_box.setMinimum(1)
        self.parallel_box.setMaximum(12)
        self.auto_album_check = QCheckBox(self.groupBox_2)
        self.auto_album_check.setObjectName(u"auto_album_check")
        self.auto_album_check.setGeometry(QRect(170, 50, 20, 31))
        self.auto_album_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.auto_album_check.setStyleSheet(u"QCheckBox {\n"
"    text-align: left;\n"
"}")
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 50, 151, 31))
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.groupBox_3 = QGroupBox(SettingDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 170, 461, 131))
        self.groupBox_3.setStyleSheet(u"QGroupBox {\n"
"    border: 2px solid #dfe6e9;\n"
"    border-radius: 5px;\n"
"    margin-top: 10px;\n"
"}\n"
"QGroupBox::title {\n"
"    top: -10px;\n"
"    left: 5px;\n"
"    padding: 2px;\n"
"}")
        self.proxy_url_line = QLineEdit(self.groupBox_3)
        self.proxy_url_line.setObjectName(u"proxy_url_line")
        self.proxy_url_line.setGeometry(QRect(110, 60, 331, 21))
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 60, 91, 21))
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.proxy_enable_check = QCheckBox(self.groupBox_3)
        self.proxy_enable_check.setObjectName(u"proxy_enable_check")
        self.proxy_enable_check.setGeometry(QRect(170, 20, 20, 31))
        self.proxy_enable_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.proxy_enable_check.setStyleSheet(u"QCheckBox {\n"
"    text-align: left;\n"
"}")
        self.label_7 = QLabel(self.groupBox_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 20, 151, 31))
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.label_8 = QLabel(self.groupBox_3)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(240, 20, 101, 31))
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.sys_proxy_check = QCheckBox(self.groupBox_3)
        self.sys_proxy_check.setObjectName(u"sys_proxy_check")
        self.sys_proxy_check.setGeometry(QRect(350, 20, 20, 31))
        self.sys_proxy_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.sys_proxy_check.setStyleSheet(u"QCheckBox {\n"
"    text-align: left;\n"
"}")
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 90, 151, 31))
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.ssl_enable_check = QCheckBox(self.groupBox_3)
        self.ssl_enable_check.setObjectName(u"ssl_enable_check")
        self.ssl_enable_check.setGeometry(QRect(170, 90, 20, 31))
        self.ssl_enable_check.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.ssl_enable_check.setStyleSheet(u"QCheckBox {\n"
"    text-align: left;\n"
"}")
        self.ok_btn = QPushButton(SettingDialog)
        self.ok_btn.setObjectName(u"ok_btn")
        self.ok_btn.setGeometry(QRect(290, 320, 75, 31))
        self.cancel_btn = QPushButton(SettingDialog)
        self.cancel_btn.setObjectName(u"cancel_btn")
        self.cancel_btn.setGeometry(QRect(380, 320, 75, 31))

        self.retranslateUi(SettingDialog)

        QMetaObject.connectSlotsByName(SettingDialog)
    # setupUi

    def retranslateUi(self, SettingDialog):
        SettingDialog.setWindowTitle(QCoreApplication.translate("SettingDialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("SettingDialog", u"ffmpeg", None))
        self.ffmpeg_path_btn.setText(QCoreApplication.translate("SettingDialog", u"...", None))
        self.label.setText(QCoreApplication.translate("SettingDialog", u"ffmpeg.exe path:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SettingDialog", u"download", None))
        self.download_path_btn.setText(QCoreApplication.translate("SettingDialog", u"...", None))
        self.label_2.setText(QCoreApplication.translate("SettingDialog", u"default directory:", None))
        self.label_3.setText(QCoreApplication.translate("SettingDialog", u"parallel:", None))
        self.auto_album_check.setText("")
        self.label_4.setText(QCoreApplication.translate("SettingDialog", u"auto create album directory:", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SettingDialog", u"network", None))
        self.label_5.setText(QCoreApplication.translate("SettingDialog", u"proxy url:", None))
        self.proxy_enable_check.setText("")
        self.label_7.setText(QCoreApplication.translate("SettingDialog", u"use proxy:", None))
        self.label_8.setText(QCoreApplication.translate("SettingDialog", u"use system proxy:", None))
        self.sys_proxy_check.setText("")
        self.label_9.setText(QCoreApplication.translate("SettingDialog", u"verify ssl:", None))
        self.ssl_enable_check.setText("")
        self.ok_btn.setText(QCoreApplication.translate("SettingDialog", u"Ok", None))
        self.cancel_btn.setText(QCoreApplication.translate("SettingDialog", u"Cancel", None))
    # retranslateUi

