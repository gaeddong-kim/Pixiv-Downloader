from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'ResizeLabel'
]

class ResizeLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self._text = text
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        width = self.width()
        metric = QFontMetrics(self.font())
        text = self._text

        if width == 0:
            self.setText('')

        elif width < metric.width(text):
            while (width < metric.width(text + '...')) and width != '': 
                text = text[:-1]

            self.setText(text + '...')

        else:
            self.setText(self._text)