# importing libraries
from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Python ")

        # setting geometry
        self.setGeometry(100, 100, 500, 400)

        # creating a QListWidget
        self.list_widget = QListWidget(self)

        # setting geometry to it
        self.list_widget.setGeometry(70, 70, 100, 150)

        # list widget items
        item1 = QListWidgetItem("A")
        item2 = QListWidgetItem("B")
        item3 = QListWidgetItem("C")

        # adding items to the list widget
        self.list_widget.addItem(item1)
        self.list_widget.addItem(item2)
        self.list_widget.addItem(item3)

        # creating a label
        self.label = QLabel("", self)
        # size
        self.label.setMinimumSize(300, 120)

        # setting geometry to the label
        self.label.setGeometry(200, 100, 300, 80)

        # making label multi line
        self.label.setWordWrap(True)

        # Create a button to test row
        self.button = QPushButton("Test Row", self)
        self.button.setGeometry(200, 50, 100, 30)

        # Connect button click to test function
        self.button.clicked.connect(lambda: self.test_row())

        # showing all the widgets
        self.show()

    def test_row(self):
        # Test row for each item
        rows = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            row = self.list_widget.row(item)
            rows.append(f"Item {item.text()}: row={row}")

        # Also test with current selected item if any
        current_item = self.list_widget.currentItem()
        if current_item:
            current_row = self.list_widget.row(current_item)
            self.label.setText(
                "Rows:\n"
                + "\n".join(rows)
                + f"\n\nCurrent item row: {current_row}"
                + f"\n count: {self.list_widget.count()}"
            )
        else:
            self.label.setText(
                "Rows:\n"
                + "\n".join(rows)
                + "\n\nNo item selected"
                + f"\n count: {self.list_widget.count()}"
            )


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
