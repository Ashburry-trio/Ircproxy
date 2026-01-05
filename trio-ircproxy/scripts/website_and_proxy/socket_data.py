#!/usr/bin/python
# -*- coding: utf-8 -*-F
from __future__ import annotations

import trio
from trio import SocketStream, SSLStream
from time import time
from random import randint
from collections import deque
from typing import Dict, Deque, Set, Union
from system_data import SystemData as system_data
from fnmatch import fnmatch
from socket import gaierror

system_data.load_settings()


# Duplicated in ..trio_ircproxy.actions.yes_no()
def yes_no(msg: str = ''):
    if not msg:
        return False
    msg = str(msg).lower()
    if msg.startswith('y') or msg.startswith('ok') or msg == '1' or msg == 'on'\
            or msg.contains('true') or msg == 'allow' or msg == 'sure' or msg == 'fine'\
            or msg.startswith('affirm') or msg == '*' or msg == 'active' or msg.startswith('enable'):
        return True
    else:
        return False


async def aclose_sockets(sc_socket: trio.SocketStream | trio.SSLStream | None = None) -> None:
    """Close both irc-server and irc-client sockets together

     @param sc_socket: only one out of the two sockets is rqeuired
     @return: None
     :rtype: None

     """
    await send_quit(sc_socket)
    return None

async def send_quit(sc_socket: trio.SocketStream | trio.SSLStream) -> None:
    """
    Function is also located in socket_data. A change here must be changed there.
    vars:
        :sc_socket: Any socket either client or server
    @return:
    """
    """Replace the quitmsg"""

    if not sc_socket:
        return
    from ..trio_ircproxy.actions import send_quit as action_send_quit
    try:
        if SocketData.which_socket[sc_socket] == 'cs':
            client_socket = sc_socket
            server_socket = SocketData.mysockets[sc_socket]
        else:
            server_socket = sc_socket
            client_socket = SocketData.mysockets[sc_socket]
    except (KeyError):
        return None
    await actions.action_send_quit(server_socket)
    return None

class SocketData:
    current_count: Dict[trio.SocketStream | trio.SSLStream, int]
    send_buffer: Dict[trio.SocketStream | trio.SSLStream, Deque[str | bytes]] = {}
    mynick: Dict[trio.SocketStream | trio.SSLStream, str] = {}
    myial: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = {}
    myial_chan: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = {}
    mychans: Dict[trio.SocketStream | trio.SSLStream, Set[str]] = {}
    mylang: Dict[trio.SocketStream | trio.SSLStream, str] = {}
    mysockets: Dict[trio.SocketStream | trio.SSLStream, trio.SocketStream | trio.SSLStream] = {}
    raw_005: Dict[trio.SocketStream | trio.SSLStream , Dict[str, str | int]] = {}
    dcc_send: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = {}
    dcc_chat: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = {}
    dcc_null: Dict[trio.SocketStream | trio.SSLStream, bool] = {}
    conn_timeout: Dict[trio.SocketStream | trio.SSLStream, int] = {}
    state: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str | int | time | Set[str]]] = {}
    login: Dict[trio.SocketStream | trio.SSLStream, str | bool] = {}
    hostname: Dict[trio.SocketStream | trio.SSLStream, str] = {}
    which_socket: Dict[trio.SocketStream | trio.SSLStream, str] = {}
    user_power: dict[str, list[trio.SocketStream | trio.SSLStream]] = {}
    msg_count_send_buffer: Dict[trio.SocketStream | trio.SSLStream, int] = {}
    @classmethod
    def create_data(cls, client_socket: trio.SocketStream | trio.SSLStream,
                    server_socket: trio.SocketStream | trio.SSLStream):
        """
        Create socket data and store all the necessary information in one location.
        Vars:
            :client_socket: The client socket.
        :server_socket: The server socket.
        """
        cls.which_socket[client_socket] = 'cs'
        cls.which_socket[server_socket] = 'ss'
        cls.login[client_socket] = ''
        cls.conn_timeout[client_socket] = None
        cls.conn_timeout[server_socket] = None
        cls.mylang[client_socket] = 'en'
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
        cls.raw_005[client_socket]["maxlist"] = "b:250"   # "bIe:250"
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
                       other_sockets: list[trio.SocketStream | trio.SSLStream] | None | False = None,
                       msg: str | bytes = '') -> bool:
        """
        Sends a raw message to a given socket.
        Args:
            to_socket (trio.SocketStream | trio.SSLStream): The socket to send the message to.
            other_socket (trio.SocketStream | trio.SSLStream | None | False, optional): The other socket to send the message to. Defaults to None.
            msg (str | bytes, optional): The message to send. Defaults to ''.
        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if not msg or not to_socket:
            return False
        with trio.fail_after(10):
            try:
                if not isinstance(msg, bytes):
                    msg = msg.encode('utf-8',errors='replace')
                if not msg.endswith(b'\n'):
                    msg += b'\n'
                await to_socket.send_all(msg)
                if other_sockets:
                    for other_socket in other_sockets:
                        if other_socket is not to_socket:
                            await other_socket.send_all(msg)
            except (trio.BrokenResourceError, trio.ClosedResourceError, gaierror,
                    trio.TooSlowError, OSError, trio.BusyResourceError, ExceptionGroup, BaseException,
                    BaseExceptionGroup):
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
            return
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
