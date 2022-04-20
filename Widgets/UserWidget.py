from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL.ImageQt import ImageQt

from Widgets.Image import *
from Widgets.Worker import *

from utils import *
from thread_pool import *
from api import api, download_manager

__all__ = [
    'UserWidget'
]

class UserWidget(QGroupBox):
    clicked = pyqtSignal(int, dict)

    def __init__(self, user_object, parent=None):
        super().__init__(parent)

        self.user_data = user_object
        self.thumb = None

        self._thumb_loaded = False

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.initUI()

    def initUI(self):
        self.image = ImageWidget(self)
        self.image.setFixedSize(80, 80)

        self.name_label = QLabel(self.user_data['name'])

        layout = QGridLayout()

        layout.addWidget(self.image, 0, 0)
        layout.addWidget(self.name_label, 0, 1)

        self.setLayout(layout)

    def setImage(self, image):
        qim = ImageQt(image)
        self.thumb = QPixmap.fromImage(qim)
        
        pixmap = self.thumb.scaledToWidth(80, Qt.SmoothTransformation)
        pixmap = crop(pixmap)

        self.image.setPixmap(pixmap)
        self._thumb_loaded = True

        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if ((self.thumb is not None) and (self.user_data is not None) and 
            (event.button() == Qt.LeftButton)):
            self.clicked.emit(2, {'pixmap': self.thumb, 'user_data': self.user_data})

    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        
        with QPainter(self) as painter:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        if not self._thumb_loaded:
            self._thumb_loaded = True

            worker = Worker(api.download_user_thumb, 
                args=(self.user_data['id'], ))
            worker.signal.finished.connect(self.setImage)

            thread_pool.start(worker)