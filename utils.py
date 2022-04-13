import datetime

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from config import conf, lang

# Constant(?)s.
generator = type((lambda:(yield))())

# Function(?)s.
def blur(img):
    scene = QGraphicsScene()
    item = QGraphicsPixmapItem()

    item.setPixmap(img)
    item.setGraphicsEffect(QGraphicsBlurEffect())
    scene.addItem(item)

    res = QPixmap(img.size())
    res.fill(Qt.transparent)
    
    with QPainter(res) as painter:
        scene.render(painter, QRectF(), QRectF(res.rect()))

    return res

def crop(img):
    res = QPixmap(img.size())
    res.fill(Qt.transparent)

    with QPainter(res) as painter:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.black)
        painter.setBrush(QBrush(img))

        painter.drawEllipse(res.rect())

    return res

def timetotext(time: datetime.datetime):
    delta = (datetime.datetime.now() - time)
    sec = (delta.days * 86400) + delta.seconds

    if sec < 60:
        return lang['time_just_before']
    elif (min := sec // 60) < 60:
        return lang['time_min_ago'].format(min)
    elif (hour := min // 60) < 24:
        return lang['time_hour_ago'].format(hour)
    elif (day := hour // 24) < 7:
        return lang['time_day_ago'].format(day)
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S')

# recolor white -> color
def recolor(pixmap: QPixmap, color: QColor):
    mask = pixmap.createMaskFromColor(Qt.transparent, Qt.MaskInColor)
    pixmap.fill(color)
    pixmap.setMask(mask)

    return pixmap