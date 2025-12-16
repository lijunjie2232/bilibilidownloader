# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_dialog.ui'
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
    QPushButton,
    QSizePolicy,
    QWidget,
)


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        if not LoginDialog.objectName():
            LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(300, 330)
        LoginDialog.setStyleSheet(
            "QDialog{\n" "	background-color: rgb(255, 255, 255);\n" "}"
        )
        self.qr_label = QLabel(LoginDialog)
        self.qr_label.setObjectName("qr_label")
        self.qr_label.setGeometry(QRect(10, 10, 280, 280))
        self.qr_label.setStyleSheet(
            "QLabel{\n"
            "	color: rgb(0, 174, 236);\n"
            "	text-aligin:center;\n"
            "	background-color: rgb(255, 255, 255);\n"
            "}"
        )
        self.qr_label.setScaledContents(True)
        self.cancel_btn = QPushButton(LoginDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setGeometry(QRect(120, 300, 60, 20))

        self.retranslateUi(LoginDialog)

        QMetaObject.connectSlotsByName(LoginDialog)

    # setupUi

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(
            QCoreApplication.translate("LoginDialog", "Dialog", None)
        )
        self.qr_label.setText("")
        self.cancel_btn.setText(
            QCoreApplication.translate("LoginDialog", "cancel", None)
        )

    # retranslateUi
