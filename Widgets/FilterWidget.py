from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Widgets.Tag import *
from Widgets.Image import *
from Widgets.Switch import *

from config import conf, lang
from utils import *
from api import api, download_manager

__all__ = [
    'SearchState',
    'FilterWidget'
]

class SearchState(int): pass

class NoArgsError(Exception): pass
class UserNotSelectedError(Exception): pass

class TagSearchBox(QGroupBox):
    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.tag_label = QLabel(lang['filter_tag'])
        self.tag_input = TagLineEdit()
        self.tag_input.returnPressed.connect(self.returnPressed)

        self.order_label = QLabel(lang['filter_order'])
        self.order_combo = QComboBox()
        self.order_combo.setAttribute(Qt.WA_TranslucentBackground)

        self.order_combo.addItem(lang['filter_order_date_a'])
        self.order_combo.addItem(lang['filter_order_date_d'])
        self.order_combo.addItem(lang['filter_order_popular'])
        self.order_combo.addItem(lang['filter_order_popular_m'])
        self.order_combo.addItem(lang['filter_order_popular_f'])

        search_box_layout = QGridLayout()
        search_box_layout.addWidget(self.tag_label, 0, 0)
        search_box_layout.addWidget(self.tag_input, 0, 1)
        search_box_layout.addWidget(self.order_label, 1, 0)
        search_box_layout.addWidget(self.order_combo, 1, 1)

        self.setLayout(search_box_layout)

    def getTags(self):
        return self.tag_input.getTags()

    def getOrder(self):
        return ['date', 'date_d', 'popular_d', 'popular_male_d', 
            'popular_female_d'][self.order_combo.currentIndex()]

    def setArgs(self, args):
        self.tag_input.extendItem(args.get('tags', self.getTags()))
        self.order_combo.setCurrentText(args.get('order', self.getOrder()))

    def getArgs(self):
        tags = self.getTags()
        if tags == []:
            raise NoArgsError(lang['alert_no_tag'],
                QColor.fromRgb(0xFF1F1F))

        return { 'tag': tags, 'order': self.getOrder() }

class FollowLatestBox(QGroupBox):
    def setArgs(self, args): pass
    def getArgs(self): return {}

class UserSearchBox(QGroupBox):
    class SelectedUserWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.initUI()

        def initUI(self):
            self.image = ImageWidget()
            self.image.setFixedSize(40, 40)

            self.name_label = QLabel()

            layout = QHBoxLayout()
            layout.addWidget(self.image)
            layout.addWidget(self.name_label)
            layout.setContentsMargins(0, 0, 0, 0)

            self.setLayout(layout)

        def setUser(self, pixmap, user):
            self.setImage(pixmap)
            self.name_label.setText(user['name'])

        def setImage(self, pixmap):
            if pixmap is not None:
                pixmap = pixmap.scaledToWidth(40, Qt.SmoothTransformation)
                pixmap = crop(pixmap)

                self.image.setPixmap(pixmap)
                self.update()

        def clear(self):
            empty_pixmap = QPixmap(40, 40)
            empty_pixmap.fill(Qt.transparent)

            self.setImage(empty_pixmap)
            self.name_label.setText('')

    returnPressed = pyqtSignal()
    cleared = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

        self._thumb = None
        self._selected_user = None

    def initUI(self):
        def clear(_):
            if self._selected_user is not None:
                empty_pixmap = QPixmap(40, 40)
                empty_pixmap.fill(Qt.transparent)

                self._selected_user = None
                self.selected_user.clear()

                self.cleared.emit()

        self.nameLabel = QLabel(lang['filter_username'])
        self.nameInput = QLineEdit()
        self.nameInput.returnPressed.connect(self.returnPressed.emit)

        self.nameInput.textChanged.connect(clear)

        self.selected_user = self.SelectedUserWidget(self)

        search_box_layout = QGridLayout()
        search_box_layout.addWidget(self.nameLabel, 0, 0)
        search_box_layout.addWidget(self.nameInput, 0, 1)
        search_box_layout.addWidget(self.selected_user, 1, 0, 1, 2)

        self.setLayout(search_box_layout)

    def getName(self):
        return self.nameInput.text()

    def setUser(self, pixmap, user):
        self._selected_user = user
        self.selected_user.setUser(pixmap, user)

    def User(self):
        return self._selected_user

    def setArgs(self, args):
        self.setUser(args['pixmap'], args['user_data'])

    def getArgs(self):
        if self.User() is None:
            if self.getName() == '':
                raise FilterWidget.NoArgsError(lang['alert_no_user'],
                    QColor.fromRgb(0xFF1F1F))
            raise UserNotSelectedError(self.getName())

        return { 'user_id': self.User()['id'] }

class TabSelector(QWidget):
    tag_icon = QPixmap('./icon/tag.png')
    latest_icon = QPixmap('./icon/latest.png')
    user_icon = QPixmap('./icon/user.png')

    selectChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._y = 0

        self._tabs = []
        self._selected = -1
        self._hovered = -1

        self._progress = 0
        self._height = 0

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)

        self.anim = QPropertyAnimation(self, b'progress', self)
        self.anim.setDuration(200)

        self.addTab(self.tag_icon, lang['filter_tag_search'])
        self.addTab(self.latest_icon, lang['filter_follow_latest'])
        self.addTab(self.user_icon, lang['filter_user_search'])

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        self._progress = progress
        self.update()

    def sizeHint(self):
        return QSize(5, 0)
        
    def addTab(self, icon, name):
        self._tabs.append((icon, name))
        if self._selected == -1:
            self._selected = 0

        self._height += 35

    def enterEvent(self, event: QMouseEvent):
        self.raise_()

        self.anim.setEndValue(1)
        self.anim.start()

    def leaveEvent(self, event: QMouseEvent):
        self.anim.setEndValue(0)
        self.anim.start()

        self._hovered = -1

    def wheelEvent(self, event: QWheelEvent):
        delta = int(event.angleDelta().y() * 0.125)
        height = self.height() - self._height

        self._y = min(0, max(self._y + delta, height))
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        y = self._y
        for i in range(len(self._tabs)):
            if QRect(0, y, 30, 35).contains(event.pos()):
                self._hovered = i
                self.update()
                break

            y += 35

    def mousePressEvent(self, event: QMouseEvent):
        y = self._y
        for i in range(len(self._tabs)):
            if QRect(0, y, 30, 35).contains(event.pos()):
                self._selected = i
                self.selectChanged.emit(i)
                self.update()
                break

            y += 35

    def paintEvent(self, event: QPaintEvent):
        font_width = 0
        font_rect = None
        font_text = ''

        opt = QStyleOption()
        opt.initFrom(self)

        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)

            fore_color = opt.palette.color(QPalette.WindowText)
            back_color = opt.palette.color(QPalette.Window)

            painter.setPen(back_color)
            for i, (icon, name) in enumerate(self._tabs):
                pix = QIcon(recolor(icon, fore_color)).pixmap(25, 25)
                pix_x = (25 - pix.width()) // 2

                x = int(self._progress * 30) - 36
                y = self._y + 35 * i

                if y + 35 < 0:        continue
                if y > self.height(): break
                
                if self._selected == i:
                    brush = back_color.lighter(200)
                    rect = QRect(x, y, 40, 35)
                    pix_pos = QPoint(10, 5)

                elif self._hovered == i:
                    font_width = QFontMetrics(self.font()).width(name)
                    font_rect = QRect(x + 45, y, font_width, 35)
                    font_text = name

                    brush = back_color.lighter(150)
                    rect = QRect(x, y, 55 + font_width, 35)
                    pix_pos = QPoint(5, 5)

                else:
                    brush = back_color
                    rect = QRect(x, y, 35, 35)
                    pix_pos = QPoint(5, 5)

                painter.fillRect(rect, brush)
                painter.drawPixmap(QPoint(x + pix_x, y) + pix_pos, pix)

            if font_rect is not None:
                painter.setPen(fore_color)
                painter.drawText(font_rect, Qt.AlignCenter, font_text)

        geo = self.geometry()
        geo.setWidth(20 + font_width + int(self._progress * 30))

        self.setGeometry(geo)

class FilterWidget(QWidget):
    # 여기도 수정하시고
    searchIllust = pyqtSignal(generator)
    searchUser = pyqtSignal(str)
    toast = pyqtSignal(str, QColor)
    clear = pyqtSignal()

    TagSearch = SearchState(0)
    FollowLatest = SearchState(1)
    UserSearch = SearchState(2)

    search_icon = QPixmap('./icon/search.png')

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tab = self.TagSearch

        self.initUI()

    def initUI(self):
        def tabChange(index):
            self.clear.emit()

            self.tab.setCurrentIndex(index)
            self._tab = SearchState(index)

            is_user_search = ((self._tab == self.UserSearch) 
                          and (self.user_search_box.User() is None))

            self.search_button.setText(
                lang['filter_user_search'] if is_user_search 
                else lang['filter_search'])

        def setFilterText(index):
            self.filter_label.setText([lang['filter_safe'], lang['filter_all'],
                lang['filter_r18']][index])

        def search():
            selected_tab = self.tab.currentWidget()
            state = self.filter_switch.state()

            try:
                search_args = selected_tab.getArgs()
            except NoArgsError as e:
                self.toast.emit(*e.args)
            except UserNotSelectedError as e:
                self.searchUser.emit(*e.args)
            else:
                search_args['mode'] = ['safe', 'all', 'r18'][state]
                self.searchIllust.emit(self.func(**search_args))

        self.tag_search_box = TagSearchBox()
        self.tag_search_box.returnPressed.connect(search)

        self.follow_latest_box = FollowLatestBox()

        self.user_search_box = UserSearchBox()
        self.user_search_box.returnPressed.connect(search)

        # 얘 수정할 것
        self.user_search_box.cleared.connect(
            lambda: self.search_button.setText(lang['filter_user_search']))

        self.selector = TabSelector(self)
        self.selector.selectChanged.connect(tabChange)

        self.search_button = QPushButton(QIcon(self.search_icon), 
            lang['filter_search'])
        self.search_button.clicked.connect(search)
        self.search_button.setSizePolicy(QSizePolicy.Ignored, 
            QSizePolicy.Ignored)

        self.filter_switch = FilterSwitch()
        self.filter_switch.valueChanged.connect(setFilterText)

        self.tab = QStackedWidget(self)
        self.tab.addWidget(self.tag_search_box)
        self.tab.addWidget(self.follow_latest_box)
        self.tab.addWidget(self.user_search_box)

        self.filter_label = QLabel(lang['filter_all'])
        self.filter_label.setAlignment(Qt.AlignCenter)
        self.filter_label.setMaximumHeight(25)
        self.filter_label.setFixedWidth(50)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.selector, 0, 0, 2, 1)
        layout.addWidget(self.tab, 0, 1, 2, 1)
        layout.addWidget(self.search_button, 0, 2, 1, 2)
        layout.addWidget(self.filter_switch, 1, 2)
        layout.addWidget(self.filter_label, 1, 3)

        self.setLayout(layout)

    def setFilter(self, tab: SearchState, args):
        self.clear.emit()

        self._tab = tab

        self.tab.setCurrentIndex(int(tab))
        self.selector._selected = int(tab)

        selected_tab = self.tab.currentWidget()
        selected_tab.setArgs(args)

        if tab == SearchState(2):
            self.search_button.setText(lang['filter_search'])

    @property
    def func(self):
        return {
            self.TagSearch: api.get_illust_list,
            self.FollowLatest: api.get_follow_latest,
            self.UserSearch: api.get_user_illust_list
        }[self._tab]

    def getIter(self):
        return self.tab.currentWidget()._iter