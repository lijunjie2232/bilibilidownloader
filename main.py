# main.py
import logging
import sys

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication

from bilibilidownloader import MainWindow, __version__


def setup_environment():
    """
    Setup application environment and configuration.
    """
    # Set application attributes before creating QApplication
    QCoreApplication.setApplicationName("BilibiliDownloader")
    # Use version from __init__.py
    QCoreApplication.setApplicationVersion(__version__)
    QCoreApplication.setOrganizationName("BilibiliDownloader")

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)


def setup_logging():
    """
    Setup application logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # Optionally add file handler
            # logging.FileHandler('bilibili_downloader.log')
        ],
    )


def main():
    """
    Main entry point for the Bilibili Downloader application.
    Initializes and runs the Qt application with enhanced setup.
    """
    # Setup environment before creating QApplication
    setup_environment()
    setup_logging()

    # Create the Qt Application
    app = QApplication(sys.argv)

    # Set application icon if available
    # app.setWindowIcon(QIcon('path/to/icon.png'))

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Execute the application
    return app.exec()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logging.exception("Application failed to start")
        logging.error(e)
        sys.exit(1)
