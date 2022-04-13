import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'Toast'
]

FPS = 120

class Toast(QDialog):
    closed = pyqtSignal()

    _timer = QTimer()
    _instances = []

    def __init__(
            self, 
            msg: str, 
            color: QColor = QColor(Qt.lightGray), 
            amplify: QSizeF = QSizeF(1, .5), 
            lifespan: int = 2500,
            parent: QWidget = None):
        
        if parent is None:
            app = QApplication.instance()
            for widget in app.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    parent = widget
                    break
        
        if parent is None:
            raise RuntimeError('Toast Error: no parent')

        super().__init__(parent)

        self._size = QFontMetrics(self.font()).size(Qt.TextSingleLine, msg)
        self._pos = parent.mapToGlobal(QPoint(
            (parent.width() - self._size.width()) // 2,
            (parent.height() - self._size.height()) // 2
        ))

        self.t = time.time()

        self.resize(self._size + QSize(20, 20))
        self.move(self._pos)

        self._color = color

        self._opacity_max = 0.8
        self._opacity = 1
        
        self._msg = msg
        self._amplify = amplify

        self.grow = lifespan * 0.1
        self.stay = lifespan * 0.8
        self.shrink = lifespan * 0.1

        while len(self._instances) >= 5:
            instance = self._instances[0]
            instance.delete()

        self._instances.append(self)
        
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | 
            Qt.Tool)

        import win32gui
        import win32con

        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) 
            | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        
        self._timer.timeout.connect(self.update)
        self._timer.start()

        self.show()

    def update(self):
        dt = int((time.time() - self.t) * 1000)

        if dt < self.grow:
            self._opacity = 1 - (1 - dt / self.grow) ** 3
        elif (dt := dt - self.grow) < self.stay:
            self._opacity = 1
        elif (dt := dt - self.stay) < self.shrink:
            self._opacity = 1 - (dt / self.shrink) ** 3
        else:
            self.delete()
            return

        height = 0
        for instance in reversed(self._instances):
            if instance == self:
                break

            height -= (instance._height() + 5)

        self.repaint()
        self.move(self._pos.x(), self._pos.y() + height)

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)

            opacity = self._opacity_max * self._opacity

            self.setWindowOpacity(opacity)

            pen_color = QColor(Qt.white)
            pen_color.setAlphaF(opacity)
            
            painter.setPen(self._color)
            painter.setBrush(self._color)

            amp = 20 * self._opacity

            w, h = (self._size.width() + amp), (self._size.height() + amp)
            x, y = (self.width() - w) / 2, (self.height() - h) / 2

            rect = QRectF(x, y, w, h)

            painter.drawRoundedRect(rect, 5, 5)

            painter.setPen(pen_color)
            painter.drawText(rect, Qt.AlignCenter, self._msg)

    def _height(self):
        return self._size.height() + (20 * self._opacity)
    
    def delete(self):
        index = self._instances.index(self)

        del self._instances[index]

        self.close()
        self.deleteLater()

Toast._timer.setInterval(1000 / FPS)