import sys
import platform
import requests

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PIL.ImageQt import ImageQt

from Widgets.Image import *
from Widgets.Worker import *
from Widgets.Loading import *
from Widgets.ResizeLabel import *

from config import conf, lang
from thread_pool import thread_pool
from utils import *
from api import api, download_manager

_platform = platform.system()
if _platform == 'Windows':
	sys.path.append('T:\\private\\Programming\\pyxiv\\api')
elif _platform == 'Linux':
	sys.path.append('/media/taeikim/DATA1 : 2TB/private/Programming/Pyxiv/api')

from PixivAPI import Illust

__all__ = [
    'IllustWidget'
]

class IllustThumbWidget(LoadingWidget, ImageWidget):
    _overlay = OverlayImageWidget()

    def __init__(self, is_r18, parent=None):
        super().__init__(parent)

        self._overlay_thumb = None

        self._progress = 0.0

        self._is_r18 = is_r18
        self._is_loading = False
        self._is_complete = False

        self.setMouseTracking(True)
        self.setLoading(True)

    def setPixmap(self, thumb: QPixmap, overlay_thumb: QPixmap):
        super().setPixmap(thumb)
        self.setLoading(False)

        self._overlay_thumb = overlay_thumb

    def setLoading(self, enable: bool):
        self._is_loading = enable

        if enable:
            self.anim.start()
        else:
            self.anim.stop()

    def setComplete(self, enable: bool):
        self._is_complete = enable
        self.update()

    def setProgress(self, progress: float):
        self._progress = progress

    def paintEvent(self, event: QPaintEvent):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)

            if self._pixmap is not None:
                pix = (
                    blur(self._pixmap) if self._is_r18 and conf['hide_r18'] 
                    else self._pixmap)

                painter.setPen(QColor.fromRgba(0xFF000000))
                painter.setBrush(QBrush(pix))
                painter.drawRoundedRect(self.rect(), 5, 5)

            if self._is_loading:
                self.paintLoading(painter)
                
                painter.setPen(Qt.white)
                painter.drawText(self.rect(), Qt.AlignCenter, 
                    f'{self._progress * 100:.0f} %')

            if self._is_complete:
                color = QColor.fromRgba(0xBF000000)

                painter.setPen(color)
                painter.setBrush(color)
                painter.drawRect(self.rect())

                icon = IllustWidget.download_complete_icon.pixmap(20, 20)
                painter.drawPixmap(5, 5, icon)
        
            if self._is_r18:
                painter.setPen(Qt.red)
                painter.setBrush(Qt.red)

                metric = QFontMetrics(QFont(self.font().family(), 8))

                size = metric.size(Qt.TextSingleLine, 'R-18') + QSize(10, 5)
                rect = QRect(QPoint(self.width() - size.width() - 5, 5), 
                    size)

                painter.drawRect(rect)

                painter.setPen(Qt.white)
                painter.drawText(rect, Qt.AlignCenter, 'R-18')

    def event(self, event: QEvent):
        if event.type() == QEvent.Enter:
            self._overlay.setPixmap(self._overlay_thumb)
            self._overlay.show()

            return True

        if event.type() == QEvent.MouseMove:
            screen_height = QApplication.primaryScreen().size().height()

            if (pos := event.globalPos()).y() + 300 > screen_height:
                self._overlay.move(pos + QPoint(20, -320))
            else:
                self._overlay.move(pos + QPoint(20, 20))

            return True

        if event.type() == QEvent.Leave:
            self._overlay.close()

            return True

        return super().event(event)

class IllustWidget(QGroupBox):
    toast = pyqtSignal(str, QColor)

    set_user = pyqtSignal(tuple)
    show_detail = pyqtSignal(Illust)
    
    download_icon = QIcon('./icon/download.png')
    download_complete_icon = QIcon('./icon/download_complete.png')

    def __init__(self, illust_object, parent=None):
        super().__init__(parent)

        self.illust_object = illust_object
        self.thumb = None

        self._thumb_loaded = False
        self._is_downloading = False

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.initUI()

    def initUI(self):
        def user_name_clicked(event: QMouseEvent):
            def func():
                image = api.download_user_thumb(
                    self.illust_object['author']['id'])
                image = QPixmap.fromImage(ImageQt(image))

                return (image, self.illust_object['author'])

            if event.button() == Qt.LeftButton:
                worker = Worker(func)
                worker.signal.finished.connect(self.set_user.emit)

                thread_pool.start(worker)

        self.image = IllustThumbWidget(self.illust_object.isR18)
        self.image.setFixedSize(80, 80)

        self.title_label = ResizeLabel(self.illust_object.title)
        
        self.author_label = ResizeLabel(self.illust_object.author.name)
        self.author_label.mousePressEvent = user_name_clicked

        self.page_count = QLabel(str(self.illust_object['pageCount']))

        date = timetotext(self.illust_object.uploadDate)

        self.dateLabel = QLabel(date, self)

        layout = QGridLayout()
        layout.setHorizontalSpacing(20)

        layout.addWidget(self.image,        0, 0, 2, 1)
        layout.addWidget(self.title_label,  0, 1, 1, 2)
        layout.addWidget(self.page_count,   0, 3, alignment=Qt.AlignRight)

        layout.addWidget(self.author_label, 1, 1)
        layout.addWidget(self.dateLabel,    1, 2, 1, 2, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def download(self, path):
        if self._is_downloading:
            self.toast.emit(
                lang['alert_already_download'].format(self.illust_object),
                Qt.red)
            return

        self._is_downloading = True

        self.image.setLoading(True)
        self.image.setComplete(False)
        self.image.setProgress(0.0)

        download_manager.addDownloading()

        def finished():
            self._is_downloading = False

            self.image.setLoading(False)
            self.image.setComplete(True)
            self.image.setProgress(0.0)

            download_manager.addComplete()

            self.toast.emit(
                lang['alert_download_complete'].format(self.illust_object), 
                QColor(Qt.lightGray))

        def callback(exception):
            if isinstance(exception, requests.exceptions.ConnectionError):
                self.toast.emit(
                    lang['alert_download_failed'].format(self.illust_object),
                    QColor(Qt.red))

                self._is_downloading = False

                self.image.setLoading(False)
                self.image.setProgress(0.0)
                self.image.setComplete(False)
                
                download_manager.addFailed()

        worker = Worker(api.download_illust, callback,
            args=(self.illust_object['id'], path), 
            kwargs={
                'dir_name':conf['dir_name'], 
                'file_name':conf['file_name'],
                'callback':self.image.setProgress
        })
        worker.signal.finished.connect(finished)

        thread_pool.start(worker)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        path = conf.get('download_path', './')
        self.download(path)

    def contextMenuEvent(self, event: QContextMenuEvent):
        # 다운로드를 맨 위까지 올려보내는가, 아니면 그냥 여기서 처리하는가?

        # 위로 올려보내게 되면 다운로드 알림의 처리가 깔끔해지고
        # 여기서 처리하게 되면 그냥 전체적으로 깔끔해지게 된다.
        # 둘 다 하면 그냥 어중간하고.

        # 에라 모르겠다 시발 그냥 여기서 하자
        def download():
            path = QFileDialog.getExistingDirectory(self, 
                lang['file_dialog_select_directory'], 
                conf.get('download_path', './'))
            if path == '': return

            conf['download_path'] = path
            self.download(path)

        def show_detail():
            self.show_detail.emit(self.illust_object)

        menu = QMenu()
        menu.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        menu.setAttribute(Qt.WA_TranslucentBackground)

        menu.addAction(self.download_icon, lang["context_download"], download)
        menu.addAction(lang["context_show_detail"], show_detail)

        menu.exec_(self.mapToGlobal(event.pos()))

    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)

        with QPainter(self) as painter:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        if not self._thumb_loaded:
            self._thumb_loaded = True

            worker = Worker(api.download_illust, 
                args=(self.illust_object['id'], ), kwargs={'thumb':True})
            worker.signal.finished.connect(self.setImage)

            thread_pool.start(worker)

    def sizeHint(self):
        return QSize(200, 100)

    def setImage(self, image):
        qim = ImageQt(image)
        self.thumb = QPixmap.fromImage(qim)
        
        self.image.setPixmap(
            self.thumb.scaledToWidth(80, Qt.SmoothTransformation),
            self.thumb.scaledToWidth(300, Qt.SmoothTransformation)
        )

        self.update()