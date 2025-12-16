from io import BytesIO
from time import sleep

import qrcode
from bilibilicore.api import Passport
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QImage, QPixmap, QIcon
from PySide6.QtWidgets import QDialog, QLabel

from bilibilidownloader.ui import Ui_LoginDialog
from bilibilidownloader.utils import connect_component, thread


class LoginDialog(QDialog, Ui_LoginDialog):
    _qr_login_finished = Signal(bool)

    def __init__(
        self,
    ):
        super(LoginDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(
            QIcon(
                ":/icon/bilibilidownloader/ui/assert/qrcode.svg",
            ),
        )
        
        self._passport = Passport()
        self._qrcode_url = None
        self._qrcode_key = None
        self.succeed = False
        self.isclosed = False
        self.init_components()
        self.init_data()

    def init_components(self):
        connect_component(
            self.cancel_btn,
            "clicked",
            self.closeDialog,
        )

    def closeDialog(self, _=None):
        if self.isclosed:
            return
        self.isclosed = True
        print("self close")
        if self.succeed:
            self.accept()
        else:
            self.reject()

    @thread
    def init_data(self):
        self.refresh_qrcode()
        self.draw_qrcode()
        self.check_qrcode()

    @thread
    def draw_qrcode(self):
        # 创建二维码图像
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=11,
            border=0,
        )
        qr.add_data(self._qrcode_url)
        img = qr.make_image(
            fill_color="#fb7299",
            back_color="white",
        )

        # 转换为 QImage -> QPixmap
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qimg = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimg).scaled(
            280,
            280,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.qr_label.setPixmap(pixmap)

    def refresh_qrcode(self):
        result = self._passport.get_qrcode()
        self._qrcode_url = result["data"]["url"]
        self._qrcode_key = result["data"]["qrcode_key"]

    @thread
    def check_qrcode(self):
        """
        if code == 0:
            # update cookie
            self.__SESSION__.cookies.update(
                resp.cookies,
            )
            return 1
        elif code == 86038:
            print("二维码已失效")
            return -1
        elif code == 86090:
            print("二维码已扫码未确认")
            return 0
        elif code == 86101:
            print("未扫码")
        else:
            raise Exception("未知错误")
        return False
        """

        # check qr code
        while (
            not self.succeed and not self.isclosed
        ):  # message_box is not closed and patience > 0
            result_code = self._passport.poll(
                {
                    "qrcode_key": self._qrcode_key,
                }
            )
            if result_code:
                # close message box
                self.succeed = True
                break
            else:
                if isinstance(result_code, bool):
                    self.setWindowTitle("扫码登录")
                elif result_code == -1:
                    self.refresh_qrcode()
                    self.draw_qrcode()
                elif result_code == 0:
                    # clear qrcode and set text
                    self.setWindowTitle("已扫描，等待确认")
            sleep(3)

        self._qr_login_finished.emit(self.succeed)
        QTimer.singleShot(
            0,
            self.accept if self.succeed else self.reject,
        )

        return
