from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from config import conf, lang

colors = {
    'dark': {
        'menu_background':'rgb(32, 32, 32)',
        'window_background':'rgb(24, 24, 24)',
        'list_background':'rgb(32, 32, 32)',
        'widget_background':'rgb(40, 40, 40)',
        'border':'rgb(56, 56, 56)',
        'tag_background':'rgb(64, 64, 64)',
        'selected_background':'rgb(192, 192, 192)',
        'text_color':'white',
        'selected_color':'rgb(48, 48, 48)'
    },
    'light': {
        'menu_background':'white',
        'window_background':'rgb(232, 232, 232)',
        'list_background':'rgb(224, 224, 224)',
        'widget_background':'rgb(216, 216, 216)',
        'border':'rgb(208, 208, 208)',
        'tag_background':'rgb(192, 192, 192)',
        'selected_background':'rgb(64, 64, 64)',
        'text_color':'black',
        'selected_color':'rgb(208, 208, 208)'
    },
}

with open(f'./stylesheet.qss', 'r') as f:
    stylesheet = f.read() % colors[conf['theme']]