from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'FlowLayout'
]

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._items = []

    def __del__(self): 
        del self._items

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def horizontalSpacing(self):
        return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect: QRect, testonly):
        left, top, right, bottom = self.getContentsMargins()
        rect = rect.adjusted(left, top, -right, -bottom)

        x, y = rect.x(), rect.y()

        line_height = 0

        for item in self._items:
            widget = item.widget()
            hspace = self.horizontalSpacing()
            vspace = self.verticalSpacing()

            if hspace == -1:
                hspace = widget.style().layoutSpacing(QSizePolicy.PushButton, 
                    QSizePolicy.PushButton, Qt.Horizontal)

            if vspace == -1:
                vspace = widget.style().layoutSpacing(QSizePolicy.PushButton, 
                    QSizePolicy.PushButton, Qt.Vertical)
            
            next_x = x + item.sizeHint().width() + hspace
            if next_x - hspace > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + vspace
                next_x = x + item.sizeHint().width() + hspace
                line_height = 0
            
            if not testonly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()