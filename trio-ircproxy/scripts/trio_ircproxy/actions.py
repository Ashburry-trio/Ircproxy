#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
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
        except (trio.Cancelled, trio.BrokenResourceError, trio.ClosedResourceError, OSError, BrokenPipeError,
                ConnectionAbortedError, ConnectionResetError, trio.TrioInternalError):
            pass


def send_join(server_socket: trio.SocketStream | trio.SSLStream, chan_with_key: str) -> None:
    """Join a channel
    vars:
        :@param server_socket: the socket to the irc-server
        :@param chan: the channel string to join on the irc-server with the chan key
        :@return: None

    """
    if not server_socket:
        return None
    circular.sc_send(server_socket, "join :" + chan_with_key)
    return None

def ss_version_reply(nick) -> str:
    """The version reply sent to the server, just the text.
    @rtype: str
        Vars:
            :@param nick: a string of the nickname to send to
            :@return: string of the version reply including NOTICE nick :version reply

    """
    return (
            "NOTICE "
            + nick
            + f" :\x01VERSION \x02Trio-ircproxy.py\x02 {VERSION_NUM} from "
            + "\x1fhttps://www.mslscript.com\x1f\x01"
    )


def ss_send_version_reply(any_sock: trio.SocketStream | trio.SSLStream, to_nick: str) -> None:
    """Send a version reply to a nickname from a socket

    :@param from_cs: the ss_socket to send the version reply to the irc server
    :@return: None
    @rtype: None

    """

    ss_socket = any_sock
    if socket_data.which_socket[ss_socket] == 'cs':
        ss_socket = socket_data.mysockets[any_sock]
    actions.sc_send(ss_socket, ss_version_reply(to_nick))


def ss_send_ctcpreply(server_socket: trio.SocketStream | trio.SSLStream, nick: str, ctcp: str, reply_str: str) -> None:
    """Send an ctcpreply to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the ctcp-reply-notice to
        :@param ctcp: the text message word to send to the nickname as the ctcp-reply-notice
        :@param reply: the text message words to reply to the ctcp-msg with a ctcp-reply-notice
        :@return: None

    """
    if not server_socket:
        return None
    ctcp_reply = f"NOTICE {nick} :\x01{ctcp} {reply_str}\x01"
    circular.sc_send(server_socket, ctcp_reply)
    return None


def ss_send_ctcp(server_socket: trio.SocketStream | trio.SSLStream, nick: str, ctcp: str) -> None:
    """Send an ctcp to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the ctcp-msg to
        :@param ctcp: the text message words to ctcp-msg to the nickname
        :@return: None

    """
    if not server_socket:
        return None
    ctcp_send = "PRIVMSG " + nick + " " + ":\x01" + ctcp + "\x01"
    sc_send(server_socket, ctcp_send)
    return None

def send_ping(sc_socket: trio.SocketStream | trio.SSLStream, msg: str = ':TIMEOUTCHECK') -> None:
    if len(msg) == 0:
        msg = ':'
    if msg[0] != ':':
        msg = ':' + msg
    sc_send(sc_socket, str('PING ' + msg).strip())

async def send_quit(sc_socket):
    from ..website_and_proxy.socket_data import SocketData
    """Replace the quitmsg"""
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
    try:
        sc_send(other_socket, quitmsg())
    except (trio.Cancelled, trio.BrokenResourceError, trio.ClosedResourceError, OSError, BrokenPipeError,
                ConnectionAbortedError, ConnectionResetError, trio.TrioInternalError):
        return
    try:
        sc_send(client_socket, quitmsg(to=client_socket))
    except (trio.Cancelled, trio.BrokenResourceError, trio.ClosedResourceError, OSError, BrokenPipeError,
            ConnectionAbortedError, ConnectionResetError, trio.TrioInternalError):
        return
    await trio.sleep(5)
    await aclose_sockets(sockets=(other_socket, client_socket))


def quitmsg(msg: str | None = None, to: Optional[socket] = None) -> str:
    """The default quit message for the app"""
    if not msg:
        # Send to server
        msg = "\x02Machine-Gun script\x02 from \x1fhttps://www.mslscript.com\x1f"
    msg = "QUIT :" + msg
    if to:
        # Send to client
        if socket_data.mynick:
            msg = ':' + socket_data.mynick[to] + "!trio-ircproxy.py@www.mslscript.com " + msg
            print("MY NICK IS : " + socket_data.mynick[to])
        else:
            return ''
    return msg



def cs_send_msg(client_socket: trio.SocketStream | trio.SSLStream, msg: str) -> None:
    """Send a server notice to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    if not client_socket or not msg:
        return None
    msg = ":*mg-script!trio-ircproxy@www.mslscript.com PRIVMSG " + socket_data.mynick[client_socket] + " :" + msg
    sc_send(client_socket, msg)
    return None

def ss_send_msg(server_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Send an msg to the nickname
    vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the notice to
        :@param msg: the text message words to send to the nickname
        :@return: None

    """
    if not server_socket or not nick or not msg:
        return None
    msg = "PRIVMSG " + nick + " :" + msg
    circular.sc_send(server_socket, msg)
    return None


def ss_send_notice(server_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Send an notice to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the notice to
        :@param msg: the text message words to send to the nickname
        :@return: None

    """
    if not server_socket or not nick or not msg:
        return None
    msg = f"NOTICE {nick} :{msg}"
    sc_send(server_socket, msg)
    return None
1

def cs_send_notice(client_socket: trio.SocketStream | trio.SSLStream, msg: str) -> None:
    """Send a server notice to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    msg = f":*mg-script!trio-ircproxy@www.mslscript.com NOTICE {nick} :{msg}"
    sc_send(client_socket, msg)
