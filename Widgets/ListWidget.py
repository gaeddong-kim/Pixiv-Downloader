from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widgets.Loading import *

__all__ = [
    'ListWidget'
]

class ListWidget(QWidget):
    class DummyWidget(LoadingWidget):
        painted = pyqtSignal()

        def __init__(self, parent=None):
            super().__init__(parent)

            self.anim.start()
            self.setFixedHeight(100)

        def paintEvent(self, event: QPaintEvent):
            super().paintEvent(event)
            self.painted.emit()

    dummyPainted = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.widget_list = []
        self.dummy = None

        self.initUI()

    def initUI(self):
        self.widget = QWidget()

        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(5, 5, 5, 5)
        self.widget_layout.addStretch()

        self.area = QScrollArea(self)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.area.setWidgetResizable(True)
        self.area.setWidget(self.widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.area)

        self.setLayout(layout)

    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)

        with QPainter(self) as painter:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def addDummy(self):
        if self.dummy is None:
            self.dummy = ListWidget.DummyWidget(self)
            self.dummy.painted.connect(self.dummyPainted.emit)

            self.widget_layout.insertWidget(0, self.dummy)
            self.update()

    def deleteDummy(self):
        if self.dummy is not None:
            self.dummy.deleteLater()
            self.dummy = None

    def addItem(self, widget):
        count = len(self.widget_list)
        self.widget_layout.insertWidget(count, widget)

        self.widget_list.append(widget)
        self.update()

    def clearItem(self):
        for widget in self.widget_list:
            widget.deleteLater()

        self.widget_list = []
        
        if self.dummy is not None:
            self.dummy.deleteLater()
            self.dummy = None