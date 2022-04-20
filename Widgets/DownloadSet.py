from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class DownloadEntry(QObject):
    progressChanged = pyqtSignal(float)
    downloadStart = pyqtSignal()
    downloadEnd = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._progress = 0

    def setProgress(self, progress):
        self._progress = progress
        self.progressChanged.emit(progress)

class DownloadSet(QObject):
    def __init__(self):
        self._dict = {}

    def add(self, id, entry):
        self._dict[id] = entry
        entry.downloadStart.emit()

    def remove(self, id):
        entry = self._dict.pop(id)
        entry.downloadEnd.emit()

    def __getitem__(self, item):
        return self._dict[item]

    def __contains__(self, id):
        return self._dict.__contains__(id)