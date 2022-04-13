from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'LoadingWidget'
]

_PI = 2880
_TAU = 5760

class LoadingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._theta = 0

        self.anim = QPropertyAnimation(self, b'theta', self)
        self.anim.setStartValue(0)
        self.anim.setEndValue(2 * _TAU)
        self.anim.setLoopCount(-1)
        self.anim.setDuration(2000)

    @pyqtProperty(int)
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, theta):
        self._theta = theta
        self.update()

    def paintLoading(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
                
        # 반투명 검은색
        color = QColor.fromRgba(0xBF000000)

        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRect(self.rect())

        painter.setPen(QPen(Qt.gray, 3))

        device = painter.device()
        x, y = device.width() // 2, device.height() // 2

        rect = QRect(x - 16, y - 16, 32, 32)

        l, r = sorted((2 * (self._theta % _TAU), self._theta))
        
        painter.drawArc(rect, l + _PI / 2, r - l)

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            if self.isVisible():
                self.paintLoading(painter)