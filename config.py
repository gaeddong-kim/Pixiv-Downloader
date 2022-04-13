import os
import json

if not os.path.isfile('conf.json'):
    with open('conf.json', 'w') as f:
        def_conf = {
            'cookie': './cookie.json',
            'thread_count': 4,
            'hide_r18': True,
            'download_path': './',
            'username': '',
            'password': '',
            'dir_name': '(%(id)d) %(title)s',
            'file_name': '%(id)d_p%(idx)d.%(ext)s',
            'lang': 'ko_KR',
            'theme': 'light'
        }
        json.dump(def_conf, f)

with open('conf.json', 'r') as f:
    conf = json.load(f)

with open('local.json', 'r', encoding='utf-8') as f:
    lang = json.load(f)[conf['lang']]