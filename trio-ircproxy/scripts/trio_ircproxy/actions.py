#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
from trio import ClosedResourceError, BusyResourceError
from pathlib import Path
import trio
import os
from ..website_and_proxy.socket_data import SocketData as socket_data

user_file_str: str = os.path.join('.', 'scripts', 'website_and_proxy', 'users.dat')
user_file = Path(user_file_str)

# Duplicated in ..website_and_proxy.socket_data.yes_no()
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


def sc_send(sc_socket: trio.SocketStream | trio.SSLStream = None, msg: str | bytes = None) -> None:
    """Relay text to client
    """
    if not sc_socket or not msg:
        return
    if not isinstance(msg, bytes):
        msg = msg.encode("utf8", errors="replace")
    msg = msg.strip()
    msg = msg + b"\r\n"
    try:
        send_buffer = socket_data.send_buffer[sc_socket]
    except KeyError:
        return
    send_buffer.append(msg)


async def aclose_sockets(sc_socket: trio.SocketStream | trio.SSLStream | None = None) -> None:
    """Close both irc-server and irc-client sockets together

     @param sc_socket: only one out of the two sockets is rqeuired
     @return: None
     :rtype: None

     """

    send_quit(sc_socket)
    return None


def send_join(server_socket: trio.SocketStream | trio.SSLStream, chan_with_key: str | None = None) -> None:
    """Join a channel
    vars:
        :@param server_socket: the socket to the irc-server
        :@param chan: the channel string to join on the irc-server with the chan key
        :@return: None

    """
    if not server_socket:
        return None
    ck_split = chan_with_key.split(' ')
    sc_send(server_socket, "JOIN " + ck_split[0] + ':' + ck_split[1:])
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
            + "\x1fhttps://www.MyProxyIP.com\x1f\x01"
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
    sc_send(ss_socket, ss_version_reply(to_nick))


def ss_send_ctcpreply(server_socket: trio.SocketStream | trio.SSLStream, nick: str, ctcp: str, reply_str: str) -> None:
    """Send an ctcpreply to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the ctcp-reply-notice to
        :@param ctcp: the text message word to send to the nickname as the ctcp-reply-notice
        :@param reply: the text message words to reply to the ctcp-msg with a ctcp-reply-notice
        :@return: None

    """
    ctcp_reply = f"NOTICE {nick} :\x01{ctcp} {reply_str}\x01"
    sc_send(server_socket, ctcp_reply)
    return None


def ss_send_ctcp(server_socket: trio.SocketStream | trio.SSLStream, nick: str, ctcp: str) -> None:
    """Send an ctcp to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the ctcp-msg to
        :@param ctcp: the text message words to ctcp-msg to the nickname
        :@return: None

    """
    if (not isinstance(server_socket, trio.SocketStream) and not isinstance(server_socket, trio.SSLStream)) \
            or not ctcp or not nick or not isinstance(nick, str) or not isinstance(ctcp, str):
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
    return None

async def send_quit(sc_socket: trio.SocketStream | trio.SSLStream) -> None:
    """
    Function is also located in socket_data. A change here must be changed there.

    @param sc_socket:
    @return:
    """
    from ..website_and_proxy.socket_data import SocketData
    """Replace the quitmsg"""
    if not sc_socket:
        return

    try:
        if SocketData.which_socket[sc_socket] == 'cs':
            client_socket = sc_socket
            other_socket = SocketData.mysockets[sc_socket]
        else:
            other_socket = sc_socket
            client_socket = SocketData.mysockets[sc_socket]
    except (KeyError):
        return None
    quitmsg(client_socket=client_socket, fto=client_socket)
    return None


def quitmsg(msg: str = None, fto = None, client_socket: trio.SocketStream | trio.SSLStream = None) -> None:
    """The default quit message for the app"""
    from ..website_and_proxy.socket_data import SocketData as socket_data
    if not msg:
        # Send to server
        msg: str = "\x02Trio-IRCProxy.py\x02"
    msg = "QUIT :" + msg
    send_all(socket_data.mysockets[client_socket], msg)
    if fto:
        # Send to client
        msg: str = ':' + socket_data.mynick[fto] + "!trio-ircproxy.py@www.myproxyip.com " + msg
        send_all(client_socket, msg=msg)
        socket_data.clear_data(client_socket)
    return None

def send_all(fto: list[trio.SocketStream | trio.SSLStream] | tuple[trio.SocketStream | trio.SSLStream] | trio.SocketStream | trio.SSLStream, msg: str) -> None:
    if isinstance(fto, list) or isinstance(fto, tuple):
        for send in fto:
            sc_send(send, msg)
    else:
        sc_send(fto, msg)
    return None


def cs_send_msg(client_socket: trio.SocketStream | trio.SSLStream, msg: str) -> None:
    """Send a privmsg to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    if (not isinstance(client_socket, trio.SocketStream) and not isinstance(client_socket, trio.SSLStream)) \
            or not msg or not nick or not isinstance(nick, str) or not isinstance(msg, str):
        return None
    msg = ":*Status!trio-ircproxy.py@www.MyProxyIP.com PRIVMSG " + socket_data.mynick[client_socket] + " :" + msg
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
    if (not isinstance(server_socket, trio.SocketStream) and not isinstance(server_socket, trio.SSLStream)) \
            or not msg or not nick or not isinstance(nick, str) or not isinstance(msg, str):
        return
    msg = "PRIVMSG " + nick + " :" + msg
    sc_send(server_socket, msg)
    return None


def ss_send_notice(server_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Send an notice to the nickname
    Vars:
        :@param server_socket: the socket to the irc-server
        :@param nick: the nickname to send the notice to
        :@param msg: the text message words to send to the nickname
        :@return: None

    """
    if (not isinstance(server_socket, trio.SocketStream) and not isinstance(server_socket, trio.SSLStream)) \
            or not msg or not nick or not isinstance(nick, str) or not isinstance(msg, str):
        return None
    msg = f"NOTICE {nick} :{msg}"
    sc_send(server_socket, msg)
    return None


1


def cs_send_notice(client_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Send a server notice to the irc-client
    vars:
        :@param client_socket: the socket to the irc-client
        :@param msg: the text message words to send to the irc-client
        :@return: None

    """
    if (not isinstance(client_socket, trio.SocketStream) and not isinstance(client_socket, trio.SSLStream)) \
            or not msg or not nick or not isinstance(nick, str) or not isinstance(msg, str):
        return None
    msg = f":*mg-script!trio-ircproxy@www.myircproxyip.com NOTICE {nick} :{msg}"
    sc_send(client_socket, msg)
    return None

