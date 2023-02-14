#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

# Change to .ini file
from configparser import ConfigParser
from os import environ
from os import path
_dir = path.dirname(path.abspath(__file__))
ini_file = path.join(_dir, '..', 'www-server-config.ini')

w3_server: ConfigParser = ConfigParser()
w3_server.read(ini_file)

if 'DEFAULT' not in w3_server:
    w3_server['DEFAULT'] = {}
if not 'url-prefix' in w3_server["DEFAULT"]:
    w3_server['DEFAULT']['url-prefix']: str = '/'
if not 'web-server-hostname' in w3_server['DEFAULT']:
    w3_server['DEFAULT']['web-server-hostname']: str = '127.0.0.1'
if not 'web-server-port' in w3_server['DEFAULT']:
    w3_server['DEFAULT']['web-server-port']: str = '80'

if 'Service' not in w3_server:
    w3_server.add_section('Service')
    w3_server['Service']['debug']: str = 'true'

if 'HOST_NAME' in environ:
    url: str = environ['HOST_NAME']
    if url not in w3_server:
        w3_server[url] = {}
        w3_server[url]['web-server-hostname']: str = url
        w3_server[url]['web-server-port']: str = '80'
        w3_server[url]['debug']: str = 'false'
        w3_server[url]['remote']: str = 'true'
        w3_server[url]['url-prefix']: str = '/'
        w3_server['DEFAULT']['using-topic-setup'] = url

with open(ini_file, 'w') as fpwrite:
    w3_server.write(fpwrite, space_around_delimiters=True)

service_ini: str = w3_server['DEFAULT']['using-topic-setup']
w3_prefix: str = w3_server[service_ini]['url-prefix'] or '/'
website_named_host: str = w3_server[service_ini]['web-server-hostname'] or '127.0.0.1'
website_port: int = int(w3_server[service_ini]['web-server-port']) or 80
