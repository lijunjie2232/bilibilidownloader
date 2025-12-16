# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
    QAction,
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
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QToolButton,
    QWidget,
)

import icon_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 768)
        self.login_op = QAction(MainWindow)
        self.login_op.setObjectName("login_op")
        self.setting_op = QAction(MainWindow)
        self.setting_op.setObjectName("setting_op")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.download_list_text = QLabel(self.centralwidget)
        self.download_list_text.setObjectName("download_list_text")
        self.download_list_text.setGeometry(QRect(10, 60, 181, 32))
        font = QFont()
        font.setPointSize(11)
        self.download_list_text.setFont(font)
        self.download_list_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_list = QListWidget(self.centralwidget)
        self.download_list.setObjectName("download_list")
        self.download_list.setGeometry(QRect(10, 100, 621, 621))
        self.download_list.setStyleSheet(
            "QListWidget::item {\n"
            "    border-bottom: 1px solid #b2bec3;\n"
            "    background-color: #fff;\n"
            "}\n"
            "QListWidget::item:hover {\n"
            "    background-color: #e1f5fe;\n"
            "}\n"
            "QListWidget::item:selected {\n"
            "    background-color: #e1f5fe;\n"
            "    border: 2px solid #fd79a8;\n"
            "}"
        )
        self.download_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.download_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.cancle_all_btn = QPushButton(self.centralwidget)
        self.cancle_all_btn.setObjectName("cancle_all_btn")
        self.cancle_all_btn.setGeometry(QRect(535, 60, 96, 32))
        self.pause_all_btn = QPushButton(self.centralwidget)
        self.pause_all_btn.setObjectName("pause_all_btn")
        self.pause_all_btn.setGeometry(QRect(425, 60, 96, 32))
        self.resume_all_btn = QPushButton(self.centralwidget)
        self.resume_all_btn.setObjectName("resume_all_btn")
        self.resume_all_btn.setGeometry(QRect(310, 60, 96, 32))
        self.head_label = QLabel(self.centralwidget)
        self.head_label.setObjectName("head_label")
        self.head_label.setGeometry(QRect(470, 10, 32, 32))
        self.head_label.setPixmap(
            QPixmap("C:/Pictures/547288f2178d80b0bba95d1c37d14b38.jpeg")
        )
        self.head_label.setScaledContents(True)
        self.link_type_selector = QToolButton(self.centralwidget)
        self.link_type_selector.setObjectName("link_type_selector")
        self.link_type_selector.setGeometry(QRect(10, 10, 100, 32))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.link_type_selector.sizePolicy().hasHeightForWidth()
        )
        self.link_type_selector.setSizePolicy(sizePolicy)
        self.link_type_selector.setMinimumSize(QSize(100, 32))
        font1 = QFont()
        font1.setPointSize(10)
        self.link_type_selector.setFont(font1)
        self.link_type_selector.setPopupMode(
            QToolButton.ToolButtonPopupMode.MenuButtonPopup
        )
        self.link_type_selector.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        self.link_type_selector.setAutoRaise(False)
        self.link_type_selector.setArrowType(Qt.ArrowType.NoArrow)
        self.link_line = QLineEdit(self.centralwidget)
        self.link_line.setObjectName("link_line")
        self.link_line.setGeometry(QRect(110, 10, 351, 32))
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.link_line.sizePolicy().hasHeightForWidth())
        self.link_line.setSizePolicy(sizePolicy1)
        self.link_line.setMinimumSize(QSize(0, 32))
        self.link_line.setMaximumSize(QSize(16777215, 32))
        self.name_label = QLabel(self.centralwidget)
        self.name_label.setObjectName("name_label")
        self.name_label.setGeometry(QRect(510, 10, 120, 32))
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.name_label.sizePolicy().hasHeightForWidth())
        self.name_label.setSizePolicy(sizePolicy2)
        self.name_label.setMinimumSize(QSize(120, 32))
        self.name_label.setMaximumSize(QSize(120, 32))
        self.name_label.setFont(font1)
        self.name_label.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 22))
        self.file_menu = QMenu(self.menubar)
        self.file_menu.setObjectName("file_menu")
        self.edit_menu = QMenu(self.menubar)
        self.edit_menu.setObjectName("edit_menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.edit_menu.menuAction())
        self.file_menu.addAction(self.login_op)
        self.edit_menu.addAction(self.setting_op)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.login_op.setText(QCoreApplication.translate("MainWindow", "logout", None))
        self.setting_op.setText(
            QCoreApplication.translate("MainWindow", "settings", None)
        )
        self.download_list_text.setText(
            QCoreApplication.translate("MainWindow", "Download List", None)
        )
        self.cancle_all_btn.setText(
            QCoreApplication.translate("MainWindow", "\u5168\u90e8\u53d6\u6d88", None)
        )
        self.pause_all_btn.setText(
            QCoreApplication.translate("MainWindow", "\u5168\u90e8\u6682\u505c", None)
        )
        self.resume_all_btn.setText(
            QCoreApplication.translate("MainWindow", "\u5168\u90e8\u5f00\u59cb", None)
        )
        self.head_label.setText("")
        self.link_type_selector.setText(
            QCoreApplication.translate("MainWindow", "video", None)
        )
        self.link_line.setText(
            QCoreApplication.translate("MainWindow", "113696558814120", None)
        )
        self.name_label.setText(
            QCoreApplication.translate("MainWindow", "Not Login", None)
        )
        self.file_menu.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.edit_menu.setTitle(QCoreApplication.translate("MainWindow", "Edit", None))

    # retranslateUi
