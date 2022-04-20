import os
import sys
import json
import platform

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widgets.Dialog import *

from config import conf, lang

_platform = platform.system()
if _platform == 'Windows':
	sys.path.append('T:\\private\\_Programming\\pyxiv\\api')
elif _platform == 'Linux':
	sys.path.append('/media/taeikim/DATA1 : 2TB/private/Programming/Pyxiv/api')

from PixivAPI import PixivAPI

# open cookie for api.
if os.path.isfile(conf['cookie']):
    with open(conf['cookie'], 'r') as f:
        cookie = json.load(f)

else:
    cookie = LoginDialog().exec()
    with open(conf['cookie'], 'w') as f:
        json.dump(cookie, f)

class DownloadManager(QObject):
    valueChanged = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        self.downloading = 0
        self.complete = 0
        self.failed = 0

        self.download_list = []
        self.complete_list = []
        self.failed_list = []

    def addDownloading(self):
        self.downloading += 1
        self.valueChanged.emit(self.downloading, self.complete, self.failed)

    def addComplete(self):
        self.complete += 1
        self.valueChanged.emit(self.downloading, self.complete, self.failed)

    def addFailed(self):
        self.failed += 1
        self.valueChanged.emit(self.downloading, self.complete, self.failed)

api = PixivAPI(cookie)
download_manager = DownloadManager()