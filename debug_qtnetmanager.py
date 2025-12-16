from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class ImageLoader(QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Image Loader")

        self.label = QLabel("Loading image...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.on_image_loaded)

        self.nam.get(QNetworkRequest(QUrl(url)))

    def on_image_loaded(self, reply):
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap

        if reply.error() == reply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.label.setPixmap(
                pixmap.scaled(
                    self.label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.label.setText(f"Failed to load image: {reply.errorString()}")


if __name__ == "__main__":
    app = QApplication([])
    loader = ImageLoader(
        "http://i2.hdslb.com/bfs/archive/a1b39c7a33c628d3581840e1d4ea5f5ce168f96d.jpg"
    )
    # set size
    loader.label.setFixedSize(600, 400)

    loader.show()
    app.exec()
