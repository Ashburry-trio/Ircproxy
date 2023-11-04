#!/usr/bin/python
# -*- coding: utf-8 -*-F
from __future__ import annotations

import trio
from time import time
from random import randint
from collections import deque
from typing import Dict, Deque, Set
from system_data import SystemData as system_data
from socket import gaierror

# Duplicated in ..trio_ircproxy.actions.yes_no()
def yes_no(msg: str = ''):
    if not msg:
        return 0
    msg = str(msg).lower()
    if msg.startswith('y') or msg.startswith('ok') or msg == '1' or msg == 'on'\
            or msg == 'true' or msg == 'allow' or msg == 'sure' or msg == 'fine'\
            or msg.startswith('affirm') or msg == '*':
        return 1
    else:
        return 0


system_data.load_settings()

async def aclose_sockets(sc_socket: trio.SocketStream | trio.SSLStream | None = None) -> None:
    """Close both irc-server and irc-client sockets together

     @param sc_socket: only one out of the two sockets is rqeuired
     @return: None
     :rtype: None

     """
    send_quit(sc_socket)
    return None

async def send_quit(sc_socket):
    """
    Function is also located in actions.py. A change here must be changed there.

    @param sc_socket:
    @return:
    """
    if not sc_socket:
        return

    if SocketData.which_socket[sc_socket] == 'cs':
        client_socket = sc_socket
        try:
            other_socket = SocketData.mysockets[sc_socket]
        except KeyError:
            return
    else:
        other_socket = sc_socket
        try:
            client_socket = SocketData.mysockets[sc_socket]
        except KeyError:
            return

    sc_send(other_socket, quitmsg())
    sc_send(client_socket, quitmsg(to=client_socket))
    await trio.sleep(5)
    try:
        socket_data.clear_data(other_socket)
        await other_socket.aclose()
    except (trio.ClosedResourceError, trio.BusyResourceError, OSError):
        pass
    try:
        socket_data.clear_data(client_socket)
        await client_socket.aclose()
    except (trio.ClosedResourceError, trio.BusyResourceError, OSError):
        pass


class SocketData:
    current_count: Dict[trio.SocketStream | trio.SSLStream | None, int | None]
    send_buffer: Dict[trio.SocketStream | trio.SSLStream | None, Deque[str | bytes | None]] = {}
    mynick: Dict[trio.SocketStream | trio.SSLStream | None, str | None] = {}
    myial: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | None]] = {}
    myial_chan: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | None]] = {}
    mychans: Dict[trio.SocketStream | trio.SSLStream | None, Set[str | None]] = {}
    mysockets: Dict[trio.SocketStream | trio.SSLStream | None, trio.SocketStream | trio.SSLStream | None] = {}
    raw_005: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | int | None]] = {}
    dcc_send: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | None]] = {}
    dcc_chat: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | None]] = {}
    dcc_null: Dict[trio.SocketStream | trio.SSLStream | None, bool | None] = {}
    conn_timeout: Dict[trio.SocketStream | trio.SSLStream | None, int | None] = {}
    state: Dict[trio.SocketStream | trio.SSLStream | None, Dict[str | None, str | int | time | Set[str] | None]] = {}
    login: Dict[trio.SocketStream | trio.SSLStream | None, str | bool | None] = {}
    hostname: Dict[trio.SocketStream | trio.SSLStream | None, str | None] = {}
    which_socket: Dict[trio.SocketStream | trio.SSLStream | None, str | None] = {}
    user_power: dict[None | str, list[trio.SocketStream | trio.SSLStream] | None] | None = {}
    msg_count_send_buffer: Dict[trio.SocketStream | trio.SSLStream | None, int | None] = {}
    @classmethod
    def create_data(cls, client_socket: trio.SocketStream | trio.SSLStream,
                    server_socket: trio.SocketStream | trio.SSLStream):
        """Create socket data,
          ...  put all data into one location
        """
        cls.which_socket[client_socket] = 'cs'
        cls.which_socket[server_socket] = 'ss'
        cls.login[client_socket] = ''
        cls.conn_timeout[client_socket] = None
        cls.conn_timeout[server_socket] = None
        cls.mysockets[client_socket] = server_socket
        cls.mysockets[server_socket] = client_socket
        cls.dcc_chat[client_socket] = {}
        cls.dcc_chat[server_socket] = {}
        cls.dcc_send[server_socket] = {}
        cls.dcc_send[client_socket] = {}
        cls.dcc_null[client_socket] = True
        cls.dcc_null[server_socket] = True
        cls.myial[client_socket] = {}
        cls.myial_chan[client_socket] = {}
        cls.mychans[client_socket] = set([])
        cls.mynick[client_socket] = "*no_nick"
        cls.raw_005[client_socket] = {}
        cls.raw_005[client_socket]["statusmsg"] = "+@"
        cls.raw_005[client_socket]["chantypes"] = "#"
        cls.raw_005[client_socket]["modes"] = 4
        cls.raw_005[client_socket]["channellen"] = 50
        cls.raw_005[client_socket]["topiclen"] = 390
        cls.raw_005[client_socket]["watch"] = 60
        cls.raw_005[client_socket]["awaylen"] = 180
        cls.raw_005[client_socket]["nicklen"] = 30
        cls.raw_005[client_socket]["prefix"] = "(ov)@+"
        cls.raw_005[client_socket]["chanlimit"] = "#:250"
        cls.raw_005[client_socket]["kicklen"] = 180
        cls.raw_005[client_socket]["maxtargets"] = 4
        cls.raw_005[client_socket]["maxlist"] = "bie:250"
        cls.raw_005[client_socket]["chanmodes"] = "b,k,l,psnmt"
        cls.raw_005[client_socket]["network"] = "no_network_" + str(randint(100, 9999))
        cls.send_buffer[server_socket] = deque()
        cls.send_buffer[client_socket] = deque()
        cls.state[client_socket] = dict()
        cls.state[client_socket]['face_nicknet'] = '[' + 'client_socket' + ']'
        cls.state[client_socket]['connected'] = 0
        cls.state[client_socket]['doing'] = 'connecting'
        cls.state[client_socket]['upper_nick'] = ''
        cls.state[client_socket]['motd_def'] = yes_no(system_data.Settings_ini['settings']['skip_motd'])

    @classmethod
    async def raw_send(cls, to_socket: trio.SocketStream | trio.SSLStream,
                       other_socket: trio.SocketStream | trio.SSLStream | None | False = None,
                       msg: str | bytes = '') -> bool:
        if not msg:
            return False
        with trio.fail_after(40):
            try:
                await trio.sleep(0)
                if not isinstance(msg, bytes):
                    msg = msg.encode()
                await to_socket.send_all(msg)
            except (trio.BrokenResourceError, trio.ClosedResourceError, gaierror,
                    trio.TooSlowError, OSError, trio.BusyResourceError):
                return False
            return True

    @classmethod
    def set_face_nicknet(cls, client_socket: trio.SocketStream | trio.SSLStream) -> None:
        face: str
        if client_socket not in cls.state or not cls.state[client_socket]['upper_nick']:
            face = '[' + 'client_socket' + ']'
        else:
            nick: str = cls.state[client_socket]['upper_nick']
            net: str = cls.raw_005[client_socket]['network']
            face = '[' + nick + '/' + net + ']'
        cls.state[client_socket]['face_nicknet'] = face
        return None

    @classmethod
    def echo(cls, client_socket, msg: str) -> None:
        if client_socket not in cls.state:
            face: str = '[' + cls.hostname[client_socket] + '] '
            print(face + msg)
        else:
            print(cls.state[client_socket]['face_nicknet'] + ' ' + msg)

    @classmethod
    def msg_to_client(cls, client_socket: trio.SocketStream | trio.SSLStream, msg: str):
        mynick = cls.mynick[client_socket]
        if msg[0] != ':':
            msg = ':' + msg
        msg = f": {system_data.Settings_ini['settings']['status_nick']} {mynick} {msg}"
        cls.send_buffer[client_socket].append(msg)


    @classmethod
    def clear_data(cls, xxs: trio.SocketStream | trio.SSLStream) -> None:
        """Remove the client_socket and server_socket from
        the dictionaries which they reside
        """

        if xxs is None:
            return
        try:
            other = cls.mysockets[xxs]
        except KeyError:
            other = None
        try:
            if cls.which_socket[xxs] == "cs":
                client_socket = xxs
                server_socket = other
            else:
                server_socket = xxs
                client_socket = other
        except KeyError:
            try:
                if cls.which_socket[other] == "cs":
                    server_socket = xxs
                    client_socket = other
                else:
                    client_socket = xxs
                    server_socket = other
            except KeyError:
                return
        del xxs
        for power in cls.user_power:
            try:
                cls.user_power[power].remove(client_socket)
            except ValueError:
                continue
        try:
            del cls.hostname[client_socket]
            del cls.which_socket[client_socket]
            del cls.which_socket[server_socket]
        except (KeyError, AttributeError):
            pass
        try:
            del cls.mychans[client_socket]
        except KeyError:
            pass
        try:
            del cls.dcc_null[server_socket]
            del cls.dcc_null[client_socket]
        except KeyError:
            pass
        try:
            del cls.mynick[client_socket]
        except KeyError:
            pass
        try:
            del cls.mysockets[client_socket]
            del cls.mysockets[server_socket]
        except KeyError:
            pass
        try:
            del cls.raw_005[client_socket]
        except KeyError:
            pass
        try:
            del cls.myial[client_socket]
        except KeyError:
            pass

        try:
            if client_socket:
                del cls.send_buffer[client_socket]
            if server_socket:
                del cls.send_buffer[server_socket]
        except KeyError:
            pass
        try:
            if client_socket:
                del cls.dcc_send[client_socket]
                del cls.dcc_chat[client_socket]
        except KeyError:
            pass
        try:
            if server_socket:
                del cls.dcc_send[server_socket]
                del cls.dcc_chat[server_socket]
        except KeyError:
            pass
        try:
            if client_socket:
                del cls.myial_chan[client_socket]
        except KeyError:
            pass
        try:
            if client_socket:
                del cls.state[client_socket]
        except KeyError:
            pass
        for uname in system_data.user_settings:
            if client_socket in system_data.user_settings[uname]:
                system_data.user_settings[uname].remove(client_socket)
                break
            if client_socket in system_data.user_name:
                del system_data.user_name[client_socket]
        return None
