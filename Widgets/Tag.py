from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

__all__ = [
    'TagWidget',
    'TagLineEdit'
]

class TagWidget(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setFont(QFont('Yu Gothic UI'))

        metric = QFontMetrics(self.font())
        size = metric.size(Qt.TextSingleLine, '#' + text) + QSize(10, 5)

        self._text = text
        self.setFixedSize(size)

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

        opt = QStyleOption()
        opt.initFrom(self)

        fore_color = opt.palette.color(QPalette.WindowText)
        back_color = opt.palette.color(QPalette.Window)

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)

            painter.setPen(back_color)
            painter.setBrush(back_color)

            painter.drawRoundedRect(self.rect(), 5, 5)

            painter.setPen(fore_color)

            painter.drawText(self.rect(), Qt.AlignCenter, '#' + self._text)
    
    def text(self):
        return self._text

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.text())

class TagLineEdit(QWidget):
    returnPressed = pyqtSignal()

    class LineEdit(QLineEdit):
        emptyBackspace = pyqtSignal()

        def keyPressEvent(self, event: QKeyEvent):
            if event.key() == Qt.Key_Backspace and self.text() == '':
                self.emptyBackspace.emit()

            super().keyPressEvent(event)

    def __init__(self, parent=None, sep=', '):
        super().__init__(parent)

        self._sep = sep
        self._item_count = 0

        self.setFixedHeight(25)
        self.initUI()

    def initUI(self):
        def delete_back():
            if self._item_count == 0:
                return

            self._item_count -= 1

            widget = self._layout.itemAt(self._item_count).widget()
            self._layout.removeWidget(widget)
            widget.deleteLater()

        def focus_out_event(event: QFocusEvent):
            if self.edit.text() != '':
                self.addItem(self.edit.text())
                self.edit.setText('')

        def text_changed(text):
            if self._sep in text:
                list = text.split(self._sep)
                self.extendItem(list[:-1])
                self.edit.setText(list[-1])

        def return_pressed():
            if (text := self.edit.text()) != '':
                self.addItem(text)

            self.edit.setText('')

            self.returnPressed.emit()

        self.edit = self.LineEdit(self)
        self.edit.emptyBackspace.connect(delete_back)
        self.edit.returnPressed.connect(return_pressed)
        self.edit.textChanged.connect(text_changed)

        self.edit.focusOutEvent = focus_out_event

        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.addWidget(self.edit)

        self.setLayout(self._layout)

    def addItem(self, text: str):
        widget = TagWidget(text, self)
        widget.clicked.connect(self.deleteItem)

        self._layout.insertWidget(self._item_count, widget)
        self._item_count += 1

    def extendItem(self, texts: list):
        for text in texts:
            self.addItem(text)

    def deleteItem(self, text: str):
        for i in range(self._item_count):
            if (widget := self._layout.itemAt(i).widget()).text() == text:
                self._layout.removeWidget(widget)
                widget.deleteLater()

        self._item_count -= 1

    def getTags(self):
        return [self._layout.itemAt(i).widget().text() 
            for i in range(self._item_count)]