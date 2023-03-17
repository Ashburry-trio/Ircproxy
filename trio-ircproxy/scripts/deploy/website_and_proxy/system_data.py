#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path
from os.path import realpath
# from os.path import dirname
from os.path import isfile
from os.path import isdir
from os import mkdir
from typing import List, Dict, Set
from hashlib import md5, sha256
from pathlib import Path
from configparser import ConfigParser
from pif import get_public_ip
import trio
import platformdirs as appdirs
import os
import json
from os import makedirs
import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))

user_file = Path(os.path.join(_dir, "users.dat"))
sysdir_path = os.path.join(appdirs.user_config_path(), "trio_ircproxy-11.01.15")
xdccdir_path = os.path.join(appdirs.user_config_path(), "trio_ircproxy-11.01.15", "xdcc_search")

makedirs(sysdir_path, exist_ok=True)
makedirs(xdccdir_path, exist_ok=True)
makedirs(os.path.join(_dir, 'settings'), exist_ok=True)
makedirs(os.path.join(_dir, 'memory'), exist_ok=True)


class SystemData:
    xdcc_chan_list: set[str] = set({})
    if not isdir(sysdir_path):
        mkdir(sysdir_path)
    if not isdir(xdccdir_path):
        mkdir(xdccdir_path)
    xdccdir_path = xdccdir_path
    sysdir_path = sysdir_path
    authfile_path: str = os.path.join(sysdir_path, "auth.json")
    fryserverfile_path: str = os.path.join(_dir, 'settings', 'fryserver.ini')
    settingsfile_path: str = os.path.join(_dir, 'settings', 'bnc_settings.ini')
    user_settings_path: str = os.path.join(_dir, 'settings', 'user_settings.ini')
    loggedinfile_path: str = os.path.join(_dir, 'memory', 'logged_in.json')
    nickhistoryfile_path: str = os.path.join(_dir, 'memory', "nicknames_history.json")
    xdcc_han_chat_file_path: str = os.path.join(xdccdir_path, "xdcc_chans_botsearch.json")
    xdcc_chans_www_file_path: str = os.path.join(xdccdir_path, "xdcc_chans_list.json")
    xbot_file_path: str = os.path.join(xdccdir_path, "xdcc_bots.json")
    xdcc_chansfile_path: str = os.path.join(xdccdir_path, "xdcc_chans.json")
    xdcc_chan_chat_file_path: str = os.path.join(xdccdir_path, "xdcc_chan_chat.json")
    xdcc_bot_list: List[str | int] = ['nick', 1000]
    # keep track of chat & list channels
    xdcc_chan_chat: dict = {}
    # count how many bots I have working in the channels
    xdcc_chan_count: dict = {}

    FryServer_json: ConfigParser = ConfigParser()
    Settings_ini: ConfigParser = ConfigParser()
    user_settings: dict[dict[str, set[trio.SocketStream | trio.SSLStream]]] = {}

    Nick_History_json: Dict[str, Dict[str, str]] = dict()
    Nick_History_json['nicknames'] = {}

    Loggedin_json: Dict[str, Dict[str, str]] = dict()
    Loggedin_json['loggedin'] = {}

    xdcc_www_chans_file_path: os.path.join(sysdir_path, "xdcc_chans.json")
    xdcc_www_chans = set()
    xdcc_www_chans.update({'#5ioE'})

    @classmethod
    def save_xdcc_bot_list(cls) -> None:
        with open(cls.xbot_file_path, 'w') as fp:
            fp.write(json.dumps(cls.xdcc_bot_list))
        return None

    @classmethod
    def save_xdcc_www_chans(cls) -> None:
        with open(cls.xdcc_www_chans_file_path, 'w') as fp:
            fp.write(json.dumps(cls.xdcc_www_chans))
        return None

    @classmethod
    def load_xdcc_bot_list(cls) -> None:
        with open(cls.xbot_file_path, 'r') as fp:
            cls.xdcc_bot_list = json.loads(fp.read())
        return None

    @classmethod
    def make_xdcc_bot_list(cls) -> None:
        if not isfile(cls.xbot_file_path):
            cls.save_xdcc_bot_list()
        return None

    @classmethod
    def make_xdcc_chan_chat(cls) -> None:
        if not isfile(cls.xdcc_chan_chat_file_path):
            cls.save_xdcc_chan_chat()
            return None
        with open(cls.xdcc_chan_chat_file_path, 'r') as wp:
            read = wp.read()
        if not read:
            cls.save_xdcc_chan_chat()
            return None
        cls.xdcc_chan_chat = json.loads(read)
        return None

    @classmethod
    def load_xdcc_chan_chat(cls) -> None:
        with open(cls.xdcc_chan_chat_file_path, 'r') as wp:
            read = wp.read()
        if not read:
            return None
        cls.xdcc_chan_chat = json.loads(read)
        return None

    @classmethod
    def save_xdcc_chan_chat(cls) -> None:
        try:
            with open(cls.xdcc_chan_chat_file_path, 'w') as wp:
                wp.write(json.dumps(cls.xdcc_chan_chat))
        except FileNotFoundError:
            print('unable to save xdcc botsearch file.')
        return None

    @classmethod
    def make_xdcc_chans(cls) -> None:
        if not isfile(cls.xdcc_chansfile_path):
            cls.save_xdcc_chans()
            return None
        with open(cls.xdcc_chansfile_path, 'r') as wp:
            read = wp.read().strip()
        if not read:
            cls.save_xdcc_chans()
            return None
        cls.xdcc_chan_list = json.loads(read)
        return None

    @classmethod
    def load_xdcc_chans(cls) -> None:
        with open(cls.xdcc_chansfile_path, 'r') as wp:
            read = wp.read().strip()
        if not read:
            cls.save_xdcc_chans()
            return None
        cls.xdcc_chan_list = json.loads(read)
        return None

    @classmethod
    def save_xdcc_chans(cls) -> None:
        try:
            with open(cls.xdcc_chansfile_path, 'w') as wp:
                wp.write(json.dumps(cls.xdcc_chan_list))
        except FileNotFoundError:
            print('unable to save xdcc chan file.')
        return None

    @classmethod
    def save_settings(cls) -> None:
        try:
            with open(cls.settingsfile_path, 'w') as wp:
                cls.Settings_ini.write(wp)
        except FileNotFoundError:
            print('unable to save settings.')
        return None

    @classmethod
    def make_settings(cls) -> None:
        try:
            if not isfile(cls.settingsfile_path):
                cls.save_settings()
                return None
            cls.load_settings()
        except FileNotFoundError:
            print('unable to make settings.')
        return None

    @classmethod
    def load_settings(cls) -> None:
        read: str
        with open(cls.settingsfile_path, 'r') as fp:
            read = fp.read()
        if not read:
            cls.save_settings()
            return None
        cls.Settings_ini.read(cls.settingsfile_path)
        try:
            cls.Settings_ini['settings']['public_ip'] = get_public_ip()
        except (UnicodeError, UnicodeWarning, UnicodeDecodeError, UnicodeEncodeError,
                UnicodeTranslateError):
            cls.Settings_ini['settings']['public_ip'] = 'unknown'
        except KeyboardInterrupt:
            try:
                sys.exit(130)
            except SystemExit:
                os._exit(130)

        return None

    @classmethod
    def save_nickhistory(cls) -> None:
        try:
            with open(cls.nickhistoryfile_path, 'w') as fp:
                fp.write(json.dumps(cls.nickhistoryfile_path))
        except FileNotFoundError:
            print('unable to save your nickname history.')
        return None

    @classmethod
    def load_nickhistory(cls) -> None:
        with open(cls.nickhistoryfile_path, 'r') as fp:
            read = fp.read()
        if not read:
            cls.save_nickhistory()
            return None
        else:
            cls.Nick_History_json = json.loads(read)
        return None

    @classmethod
    def make_nickhistory(cls):
        try:
            cls.load_nickhistory()
        except FileNotFoundError:
            cls.save_nickhistory()
        return None

    @classmethod
    def nickhistory_add(cls, nick) -> None:
        """Add a nickname to the nickhistory file

            vars:
                :@param nick: the nickname to add to the history
        """
        if nick in cls.Nick_History_json['nicknames']:
            # move the old nickname to the end of the list
            del cls.Nick_History_json['nicknames'][nick]

        cls.Nick_History_json['nicknames'][nick] = nick

        while 11 - len(cls.Nick_History_json) < 0:
            for nick in cls.Nick_History_json:
                del cls.Nick_History_json['nicknames'][nick]
                break
        cls.save_nickhistory()
        return None

    @classmethod
    def make_user_file(cls) -> None:
        newlogin = 'user:email@no-host.com:admin:' + sha256(b'pass').hexdigest() + '\n'
        do_write = False
        if user_file.is_file():
            with open(user_file, 'r') as sfopen:
                sfread = sfopen.read()
                if sfread:
                    do_write = True
        if not do_write:
            with open(user_file, 'w') as sfopen:
                sfopen.write(newlogin)

        return None

    @classmethod
    def save_fryfile(cls) -> None:
        try:
            with open(cls.fryserverfile_path, 'w') as wpp:
                cls.FryServer_json.write(wpp)
        except FileNotFoundError:
            print('unable to save fry file.')
        return None

    @classmethod
    def make_fryfile(cls) -> None:
        if not isfile(cls.fryserverfile_path):
            cls.save_fryfile()
        else:
            cls.load_fryfile()

    @classmethod
    def load_fryfile(cls) -> None:
        with open(cls.fryserverfile_path, 'r') as fp:
            read = fp.read()
            if not read:
                cls.save_fryfile()
            else:
                cls.FryServer_json.read(cls.fryserverfile_path)
                cls.FryServer_json.add_section('ip_list')
        return None
