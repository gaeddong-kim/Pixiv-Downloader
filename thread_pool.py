from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from config import conf

thread_pool = QThreadPool()
thread_pool.setMaxThreadCount(conf['thread_count'])