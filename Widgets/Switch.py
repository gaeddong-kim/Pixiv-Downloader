from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'Switch',
    'FilterSwitch'
]

class Switch(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, step, state=0, parent=None):
        super().__init__(parent)

        if step <= 1:
            raise RuntimeError('step must bigger than 1')

        self._step = step
        self._state = state
        self._thumb_pos = state

        self.setFixedSize(50, 25)

        self._anim = QPropertyAnimation(self, b'thumbPos', self)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.setDuration(200)

    @pyqtProperty(float)
    def thumbPos(self):
        return self._thumb_pos

    @thumbPos.setter
    def thumbPos(self, pos):
        self._thumb_pos = pos
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self._anim.state() != QPropertyAnimation.Running:
            self.setState(int(event.pos().x() * self._step / self.width()))

    def setState(self, state):
        if self._state != state:
            self._state = state
            self._anim.setEndValue(self._state)
            self._anim.start()

            self.valueChanged.emit(self._state)

    def state(self):
        return self._state

    # 색을 바꾸려면 이 함수를 오버라이딩하면 된다.
    def getColor(self, state):
        return QColor('#AAAAAA')

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)

            w, h = self.width(), self.height()

            color = self.getColor(self._state)

            painter.setPen(Qt.transparent)
            painter.setBrush(color)

            rect = QRectF((w - h) * .3, h * .2, w * .4 + h * .6, h * .6)
            painter.drawRoundedRect(rect, h * .3, h * .3)

            x_pos = w * .4 * self._thumb_pos / (self._step - 1)

            thumb = QRectF(-h * .4, h * .1, h * .8, h * .8)
            thumb.adjust(x_pos + w * .3, 0, x_pos + w * .3, 0)

            painter.setPen(color.lighter())
            painter.setBrush(color.lighter())

            painter.drawEllipse(thumb)

class FilterSwitch(Switch):
    colors = [
        QColor("#00B0FF"), # Safe
        QColor("#AAAAAA"), # All
        QColor("#FF0000")  # R-18
    ]

    def __init__(self, parent=None):
        super().__init__(3, 1, parent)

    def getColor(self, state):
        return self.colors[state]