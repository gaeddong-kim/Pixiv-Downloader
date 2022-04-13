from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'ImageWidget',
    'OverlayImageWidget'
]

class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None

    def setPixmap(self, thumb: QPixmap):
        self._pixmap = thumb
        self.update()
        
    def paintEvent(self, event: QPaintEvent):
        if self._pixmap is not None:
            with QPainter(self) as painter:
                painter.setRenderHint(QPainter.Antialiasing)
                painter.drawPixmap(self.rect(), self._pixmap, 
                    self._pixmap.rect())

class OverlayImageWidget(ImageWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)

        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.CustomizeWindowHint 
            | Qt.Tool)

        import win32gui
        import win32con

        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)