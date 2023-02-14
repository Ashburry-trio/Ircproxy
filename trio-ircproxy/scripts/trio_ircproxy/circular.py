#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional, Union
from pathlib import Path
import trio
import os
from ..website_and_proxy.socket_data import SocketData as socket_data

user_file_str: str = os.path.join('.', 'scripts', 'website_and_proxy', 'users.dat')
user_file = Path(user_file_str)


def sc_send(sc_socket: trio.SocketStream | trio.SSLStream, msg: str | bytes) -> None:
    """Relay text to client
    """
    if not sc_socket:
        return
    if not isinstance(msg, bytes):
        msg = msg.encode("utf8", errors="replace")
    msg = msg.strip()
    msg = msg + b"\n"
    try:
        send_buffer = socket_data.send_buffer[sc_socket]
    except KeyError:
        return
    send_buffer.append(msg)


def cs_send_notice(client_socket: trio.SocketStream | trio.SSLStream, msg: str) -> None:
    """Send a server notice to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    if not client_socket or not msg:
        return None
    msg = ":trio-ircproxy.py NOTICE " + socket_data.mynick[client_socket] + " :" + msg
    sc_send(client_socket, msg)
    return None

def cs_send_msg(client_socket: trio.SocketStream | trio.SSLStream, msg: str) -> None:
    """Send a server notice to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    if not client_socket or not msg:
        return None
    msg = ":trio-ircproxy.py PRIVMSG " + socket_data.mynick[client_socket] + " :" + msg
    sc_send(client_socket, msg)
    return None


async def send_quit(sc_socket):
    from ..website_and_proxy.socket_data import SocketData
    """Replace the quitmsg"""
    if not sc_socket:
        return

    print('send quit: ' + SocketData.which_socket[sc_socket])
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
    await trio.sleep(0.8)
    await aclose_sockets(sockets=(other_socket, client_socket))




def send_ping(sc_socket: trio.SocketStream | trio.SSLStream, msg: str = ':TIMEOUTCHECK') -> None:
    if len(msg) == 0:
        msg = ':'
    if msg[0] != ':':
        msg = ':' + msg
    sc_send(sc_socket, str('PING ' + msg).strip())


def quitmsg(msg: Optional[str] = None, to: Optional[socket] = None) -> Optional[str]:
    """The default quit message for the app"""
    if not msg:
        # Send to server
        msg = "\x02trio-ircproxy.py\x02 from \x1fhttps://ashburry.pythonanywhere.com\x1f"
    msg = "QUIT :" + msg
    if to:
        # Send to client
        if socket_data.mynick[to]:
            msg = ':' + socket_data.mynick[to] + "!identd@ashburry.pythonanywhere.com " + msg
            print(" MY NICK IS : " + socket_data.mynick[to])
        else:
            return ''
    return msg


async def aclose_sockets(sockets=None) -> None:
    """Takes a list of sockets and closes them

        vars:
            :param sockets: a list of sockets to close
            :returns: None
    """
    if not sockets:
        return
    for sock in sockets:
        if not sock:
            continue
        try:
            await sock.aclose()
        except (AttributeError, OSError, BrokenPipeError):
            return



