#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

from configparser import ConfigParser
from os import path
_dir = path.dirname(path.abspath(__file__))

ini_file = path.join(_dir, '..', 'www-server-config.ini')
w3_server: ConfigParser = ConfigParser()
w3_server.read(ini_file)

topic = w3_server['DEFAULT']['using-topic-setup']
if topic not in w3_server:
    print("Invalid .\scripts\www\www-server-config.ini under topic DEFAULT for item using-topic-setup does not exist")
    raise(AttributeError)

Debug = w3_server[topic]['debug']
Debug = Debug.lower()
Debug = 'false' if Debug != 'true' else 'true'
running_os = w3_server[topic]['running_os'].lower()
running_os = 'windows' if running_os != 'linux' else 'linux'
w3_server[topic]['running_os'] = running_os

with open(ini_file, 'w') as fpwrite:
    w3_server.write(fpwrite, space_around_delimiters=True)

# Choose your operating system, either windows or linux:
# set in trio-ircproxy-main\trio-ircproxy\scripts\www\www-server-config.ini
# running_os = 'windows'
# running_os = 'linux'

APP_DIR: list[str] = ['']
STATIC_DIR: list[str] = ['']
