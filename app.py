import os
import sys
import json

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# 스레드가 최대 네 개이므로 네 개의 작업이 이미 수행중이라면 이후 추가되는 작업들이 다운로드를 위한 준비작업조차 실행되지 않는 경우가 잦다.
# 토스트에서 parent가 NoneType일 때 터지는 문제도 고쳐야 한다. 아무래도 activeWindow를 고쳐야 할 것으로 보임.
# 이거 고쳤는지 기억이 안 난다.

# 로딩 순서
#     1. conf.py, api.py 등 위젯 이전에 로딩되는 파일들
#     2. Widgets.py에 포함된 위젯 파일들
#     3. 앱

# QT default settings.
os.environ['QT_DEVICE_PIXEL_RATIO'] = '0'
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'
os.environ['QT_SCALE_FACTOR'] = '1'

app = QApplication(sys.argv)

from utils import *
from config import conf, lang
from thread_pool import thread_pool
from api import api, download_manager
from colors import stylesheet

app.setStyleSheet(stylesheet)

from Widgets.Widgets import *

download_set = DownloadSet()

IllustWidget.download_set = download_set

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._append = True

        self._fn = None
        self._args = ()

        self._finished = None

        self.initUI()
   
    def initUI(self):
        def download(illust_object, path):
            id = illust_object.id

            download_manager.addDownloading()

            def finished():
                download_set.remove(id)
                download_manager.addComplete()

                self.showToast(
                    lang['alert_download_complete'].format(illust_object), 
                    QColor(Qt.lightGray)
                )

            def exception_handle(exception):
                download_set.remove(id)
                download_manager.addFailed()

                self.showToast(
                    lang['alert_download_failed'].format(illust_object),
                    QColor(Qt.red)
                )

            worker = Worker(api.download_illust, exception_handle,
                args=(illust_object.id, path),
                kwargs = {
                    'dir_name': conf['dir_name'],
                    'file_name': conf['file_name'],
                    'callback': download_set[id].setProgress
                }
            )
            worker.signal.finished.connect(finished)

            thread_pool.start(worker)

        def search_from_widget(state: int, args: dict):
            self.filter.setFilter(SearchState(state), args)

        def search_illust(gen):
            def finished(item_list):
                for item in item_list:
                    widget = IllustWidget(item)

                    widget.toast.connect(self.showToast)
                    widget.download.connect(download)

                    widget.search_from_widget.connect(search_from_widget)

                    self.widget_list.addItem(widget)

                self._append = True

            self._fn = next
            self._args = (gen, )

            self._finished = finished

            thread_pool.waitForDone()

            self.widget_list.clearItem()
            self.widget_list.addDummy()

        def search_user(user_name):
            def finished(user_list):
                for user in user_list:
                    widget = UserWidget(user)
                    widget.clicked.connect(search_from_widget)

                    self.widget_list.addItem(widget)
                
                self.widget_list.deleteDummy()
                self._append = True

            self._fn = api.get_user_by_name
            self._args = (user_name, )

            self._finished = finished

            thread_pool.waitForDone()

            self.widget_list.clearItem()
            self.widget_list.addDummy()

        def appendResult():
            def callback(exception):
                if isinstance(exception, StopIteration):
                    self.widget_list.deleteDummy()
                else:
                    raise exception

                self._append = True

            if self._append:
                self._append = False

                worker = Worker(self._fn, callback, args=self._args)
                worker.signal.finished.connect(self._finished)

                thread_pool.start(worker)

        def clear():
            thread_pool.waitForDone()
            self.widget_list.clearItem()

        self.filter = FilterWidget(self)
        self.filter.searchIllust.connect(search_illust)
        self.filter.searchUser.connect(search_user)
        self.filter.toast.connect(self.showToast)
        self.filter.clear.connect(clear)

        self.widget_list = ListWidget(self)
        self.widget_list.dummyPainted.connect(appendResult)

        layout = QVBoxLayout()
        layout.addWidget(self.filter)
        layout.addWidget(self.widget_list)
        layout.setContentsMargins(5, 5, 5, 5)

        self.setLayout(layout)

    def showToast(self, msg, color):
        Toast(msg, color, parent=self)

class Menu(QMenu):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def closeEvent(self, e):
        self.main_widget.close()

        thread_pool.waitForDone()

        with open('conf.json', 'w') as f:
            json.dump(conf, f)

        super().closeEvent(e)

    def initUI(self):
        def setStatusBar(download, complete, failed):
            if download == (complete + failed):
                msg = lang['status_download_complete'].format(failed, complete, 
                    download)
            else:
                msg = lang['status_download_now'].format(failed, complete, 
                    download)
            
            status_label.setText(msg)

        def showPreferenceWindow():
            PreferenceDialog().exec()

        status_label = QLabel(lang['status_no_download'])

        menu_bar = self.menuBar()
        
        status_bar = self.statusBar()
        status_bar.addWidget(status_label)

        download_manager.valueChanged.connect(setStatusBar)

        opt = menu_bar.addMenu(lang['option'])

        pre = opt.addAction(lang['preference'])
        pre.triggered.connect(showPreferenceWindow)

        self.main_widget = MainWidget()

        self.setCentralWidget(self.main_widget)

        self.setWindowIcon(QIcon('./icon/pixiv.png'))
        self.setWindowTitle("pixiv search")

        self.setMinimumSize(300, 400)
        self.setGeometry(0, 0, 300, 400)

        self.show()

ex = MainWindow()
sys.exit(app.exec_())