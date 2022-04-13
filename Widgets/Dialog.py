import sys
import platform

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widgets.Tag import *
from Widgets.Switch import *
from Widgets.Layout import *
from Widgets.Worker import *
from Widgets.Loading import *

from config import conf, lang
from thread_pool import thread_pool

__all__ = [
    'PreferenceDialog',
    'IllustDialog',
    'LoginDialog'
]

_platform = platform.system()
if _platform == 'Windows':
	sys.path.append('T:\\private\\Programming\\pyxiv\\api')
elif _platform == 'Linux':
	sys.path.append('/media/taeikim/DATA1 : 2TB/private/Programming/Pyxiv/api')

from PixivAPI import get_cookie

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.cookie = None
        self.initUI()

    def initUI(self):
        def login():
            self.layout().setCurrentIndex(1)

            self.loading.setVisible(True)
            self.loading.anim.start()

            conf['username'] = self.username_input.text()
            conf['password'] = self.password_input.text()

            def finished(res):
                if res == None:
                    self.layout().setCurrentIndex(0)

                    self.loading.setVisible(False)
                    self.loading.anim.stop()

                else:
                    self.cookie = res
                    self.close()

            worker = Worker(get_cookie, 
                args=(conf['username'], conf['password']))
            worker.signal.finished.connect(finished)

            thread_pool.start(worker)

        self.username_label = QLabel(lang['login_username'])
        self.username_input = QLineEdit(conf.get('username', ''))

        self.password_label = QLabel(lang['login_password'])
        self.password_input = QLineEdit(conf.get('password', ''))
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton(lang['login_login'])
        self.login_button.clicked.connect(login)

        self.loading = LoadingWidget(self)
        self.loading.setVisible(False)

        layout = QGridLayout()
        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.username_input, 0, 1)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(self.login_button, 2, 0, 1, 2)

        layout.setContentsMargins(5, 5, 5, 5)

        widget = QWidget()
        widget.setLayout(layout)

        stack_layout = QStackedLayout()
        stack_layout.addWidget(widget)
        stack_layout.addWidget(self.loading)
        stack_layout.setCurrentIndex(0)

        self.setLayout(stack_layout)
        self.show()

    def exec(self):
        super().exec()
        return self.cookie

class InformationWidget(QWidget):
    info_icon = QIcon('././icon/info.png')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(20, 20)

    def paintEvent(self, event: QPaintEvent):
        width = height = min(self.width() - 10, self.height() - 10)
        pix = self.info_icon.pixmap(width, height)

        with QPainter(self) as painter:
            painter.drawPixmap((self.width() - width) // 2, 
                (self.height() - height) // 2, pix)

class FileDialogButton(QPushButton):
    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)

        with QPainter(self) as painter:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
            painter.setRenderHint(QPainter.Antialiasing)

            rect = QRect(-1, -1, 2, 2)

            for i in range(1, 4):
                x, y = int(self.width() * i / 4), self.height() // 2
                painter.fillRect(rect.adjusted(x, y, x, y), QBrush(Qt.white))

class FileDialogLineEdit(QWidget):
    textChanged = pyqtSignal(str)

    def __init__(self, default='C:\\', parent=None):
        super().__init__(parent)

        self._path = default
        self.initUI()

    def initUI(self):
        def file_dialog():
            path = QFileDialog.getExistingDirectory(self, '디렉토리를 선택하세요',
                self._path)

            if path != '':
                self._path = path
                self.edit.setText(path)

        self.edit = QLineEdit(self._path)
        self.edit.textChanged.connect(self.textChanged.emit)
        self.edit.setStyleSheet('border: none; background: transparent;')

        self.button = FileDialogButton()
        self.button.clicked.connect(file_dialog)
        self.button.setStyleSheet('border: none; background: transparent;')

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.edit)
        layout.addSpacerItem(self.spacer)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        self.setFixedHeight(self.edit.height())
        self.button.setFixedSize(self.height(), self.height())
    
    def paintEvent(self, event: QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)

        with QPainter(self) as painter:
            self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

class PreferenceDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        def hideR18Changed(state: int):
            if state == 0: # Safe
                conf['hide_r18'] = True
                self.hide_r18_label.setText(lang['preference_hide_r18'])
            else:
                conf['hide_r18'] = False
                self.hide_r18_label.setText(lang['preference_show_r18'])
        
        def downloadPathChanged(text: str):
            conf['download_path'] = text

        def dirChanged(text):
            conf['dir_name'] = text

        def fileChanged(text):
            conf['file_name'] = text
        
        self.hide_r18_label = QLabel()
        if conf['hide_r18']:
            self.hide_r18_label.setText(lang['preference_hide_r18'])
        else:
            self.hide_r18_label.setText(lang['preference_show_r18'])

        self.hide_r18 = Switch(2, 0 if conf['hide_r18'] else 1)
        self.hide_r18.valueChanged.connect(hideR18Changed)

        self.hide_r18_info = InformationWidget()
        self.hide_r18_info.setToolTip(lang['preference_hide_r18_tooltip'])

        self.download_path_label = QLabel(lang['preference_download_path'])
        self.download_path_input = FileDialogLineEdit(
            conf['download_path'])
        self.download_path_input.textChanged.connect(downloadPathChanged)

        self.dir_label = QLabel(lang['preference_directory_format'])
        self.dir_input = QLineEdit(conf['dir_name'])
        self.dir_input.textChanged.connect(dirChanged)

        self.dir_info = InformationWidget()
        self.dir_info.setToolTip(
            lang['preference_directory_format_tooltip'])

        self.file_label = QLabel(lang['preference_file_format'])
        self.file_input = QLineEdit(conf['file_name'])
        self.file_input.textChanged.connect(fileChanged)

        self.file_info = InformationWidget()
        self.file_info.setToolTip(lang['preference_file_format_tooltip'])

        basic_layout = QGridLayout()
        
        basic_layout.addWidget(self.hide_r18, 0, 0)
        basic_layout.addWidget(self.hide_r18_info, 0, 1)
        basic_layout.addWidget(self.hide_r18_label, 0, 2)

        basic_layout.addWidget(self.download_path_label, 1, 0, 1, 2)
        basic_layout.addWidget(self.download_path_input, 1, 2)

        basic_layout.addWidget(self.dir_label, 2, 0)
        basic_layout.addWidget(self.dir_info, 2, 1)
        basic_layout.addWidget(self.dir_input, 2, 2)

        basic_layout.addWidget(self.file_label, 3, 0)
        basic_layout.addWidget(self.file_info, 3, 1)
        basic_layout.addWidget(self.file_input, 3, 2)

        self.basic = QGroupBox()
        self.basic.setLayout(basic_layout)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, 
            QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(self.basic)
        layout.addSpacerItem(spacer)

        self.setLayout(layout)

class IllustDialog(QDialog):
    clicked = pyqtSignal(str)

    def __init__(self, illust, parent=None):
        super().__init__(parent)
        
        self.text_edit = QTextBrowser(self)
        self.text_edit.setAcceptRichText(True)
        self.text_edit.setOpenExternalLinks(True)
        self.text_edit.setText(
            f"{illust['title']} ({illust['id']})\n" 
            + f"author: {illust['author']['name']}\n"
            + f"type: {['illust', 'manga', 'ugoira'][illust['illustType']]}"
        )
        self.text_edit.append(
            f"<a href=\"https://pixiv.net/artworks/{illust['id']}\">Pixiv link</a>"
        )

        self.tag_layout = FlowLayout()
        for tag in illust['tags']:
            tag_widget = TagWidget(tag)
            tag_widget.clicked.connect(self.clicked.emit)

            self.tag_layout.addWidget(tag_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.addLayout(self.tag_layout)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Ignored, 
            QSizePolicy.Expanding))