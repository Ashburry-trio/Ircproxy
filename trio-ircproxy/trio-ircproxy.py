#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Copyright (c) 2022, sire master gi Kenggi Peters phd. ret.

This is an async IRC proxy server. It augments the irc
clients server connection; adding functionality. It also allows
communicating to the pythonanywhere.com website server (eventually) at www.mslscript.com.
The proxy itself is interfaced by an irc client by using your 127.0.0.1 ip
for proxy server hostname/ip with the port number 4321 and default
login username/password is "user : pass"
in your irc client. for help type "/raw proxy-help" or maybe
"/quote proxy-help" or just "/proxy-help" with your irc client
after connecting to any irc server through the proxy server.

Read the readme.md file and get help in #5ioE on Undernet.
This is a pre-alpha (work in progress), don't expect it to
function properly, however it will
(not)function safely at best.

You may use this with a znc (bounce) service however your
proxy server functionaltiy will only work while a client is connected
through the proxy server.
You must run; in the terminal:
    'cd Documents"
    "unzip -d trio-ircproxy-main.zip .  (<- Notice the dot at the end)
    "cd trio-ircproxy-main"

Windows:
    "install.bat -3.11"  -+-+- (just once, forever. USe your hihgest installed python version)
    "runproxy.bat"
        or
    "runproxy.bat"


use the install.bat -3.11 if you are on windows with Python 3.11. It just sets up venv and
 installs pip, upgrades pip, and installs requirements.txt.
 You also have runproxy.bat which is a shortcut to trio-ircproxy\venv\Scripts\activate.bat and then
  "python.exe trio-ircproxy\trio-ircproxy.py"


Linux:
    cd trio-ircproxy-main
    python3.11 -m venv ./trio-ircproxy/venv
    source ./trio-ircproxy/venv/bin/activate
    pip3 install -r ./trio-ircproxy/requirements.txt
#  If using Linux for Windows (Cygwin) change /bin/ to /Scripts/
#  After executing the above commands you onnly need to execute the following
#  two commands to run the proxy server.
    source ./trio-ircproxy/venv/bin/activate
    python ./trio-ircproxy/trio-ircproxy.py

I need to create an install script for Linux and the runproxy.bat for Linux
"""

from __future__ import annotations

import ssl

import trio
from base64 import b64decode
from configparser import ConfigParser
from fnmatch import fnmatch
from os import chdir
from os import path
from os.path import dirname
from os.path import expanduser
from os.path import realpath
from pendulum import duration
from pif import get_public_ip
from random import randint

from scripts.trio_ircproxy import actions
from scripts.trio_ircproxy import ial
from scripts.trio_ircproxy import proxy_commands
from scripts.trio_ircproxy import xdcc_system
from scripts.website_and_proxy import Settings_ini
from scripts.website_and_proxy.socket_data import SocketData as socket_data
from scripts.website_and_proxy.socket_data import aclose_sockets
from scripts.website_and_proxy.system_data import SystemData as system_data
from scripts.website_and_proxy.users import validate_login, verify_user_pwdfile
# from sys import excepthook
# from sys import exc_info
from socket import gaierror
from ssl import create_default_context, SSLContext
from ssl import Purpose
from sys import argv
from threading import Timer
from time import time
from typing import Deque, Any, Coroutine
from chardet import detect
import sys
import os
from cryptography.fernet import Fernet

_dir = path.dirname(path.abspath(__file__))
chdir(realpath(dirname(expanduser(argv[0]))))

VERSION_NUM = "PEACE"


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def colourstrip(data: str) -> str:
    """Strips the mIRC colour codes from the text in data
        vars:
            :@param data: A string of text that contains mSL colour codes
            :@return: string without color codes

    """
    find = data.find("\x03")
    while find > -1:
        done = False
        data = data[:find] + data[find + 1:]
        if len(data) <= find:
            done = True
        try:
            if done:
                break
            if not int(data[find]) > -1:
                raise ValueError("Not-an-Number")
            data = data[:find] + data[find + 1:]
            try:
                if not int(data[find]) > -1:
                    raise ValueError("Not-an-Number")
            except IndexError:
                break
            except ValueError:
                data = data[:find] + data[find + 1:]
                continue
            data = data[:find] + data[find + 1:]
        except (ValueError, IndexError):
            if not done:
                if data[find] != ",":
                    done = True
        if (not done) and (len(data) >= find + 1) and (data[find] == ","):
            try:
                data = data[:find] + data[find + 1:]
                if not int(data[find]) > -1:
                    raise ValueError("Not-an-Number")
                data = data[:find] + data[find + 1:]
                if not int(data[find]) > -1:
                    raise ValueError("Not-an-Number")
                data = data[:find] + data[find + 1:]
            except ValueError:
                pass
            except IndexError:
                break
        find = data.find("\x03")
    data = data.replace("\x02", "")
    data = data.replace("\x1d", "")
    data = data.replace("\x1f", "")
    data = data.replace("\x16", "")
    data = data.replace("\x0f", "")
    data = data.replace("\x1e", "")
    return data


async def exploit_triggered(client_socket: trio.SSLStream | trio.SocketStream,
                            server_socket: trio.SSLStream | trio.SocketStream):
    socket_data.echo(client_socket, 'There was a exploit attempt by IRC network.')
    await actions.send_quit(server_socket)


def check_mirc_exploit(proto: str) -> bool:
    """Verifies that the nickname portions of the protocol
    does not contain any binary data.
        Vars:
            :@param proto: The text before the second : hopefully a nickname or channel name.
            :@return: True if there is binary data and False if it is clean.
    """
    proto: str = str(proto)
    proto = proto.strip(':')
    proto = proto.lower()
    proto_split: list[str, ...] = proto.split(' ')
    nick: bool = False
    if len(proto_split) > 1 and (proto_split[1] == '004' or proto_split[1] == '322'):
        return False
    if (len(proto_split) > 1 and proto_split[1] == 'nick') or proto_split[0] == 'nick':
        nick = True
    for let in str(proto):
        if ord(let) == 58 and nick is False:
            return False
        if ord(let) in (1, 3, 32, 31, 2, 22, 10, 13, 15, 33, 42):
            continue
        if ord(let) < 29 or ord(let) > 10000:
            spacer = False
            start = proto.find(let)
            while spacer is False:
                start -= 1
                if proto[start] == chr(32) or start <= 0:
                    return True
                if proto[start] == '#':
                    return False
            return True
    return False


def is_socket(xs: trio.SocketStream | trio.SSLStream) -> bool:
    """Returns True if the socket is sane.
        vars:

        :@param xs: The socket to check for sanity
        :@return: bool if the parm xs is a socket return True

    """
    if not isinstance(xs, trio.SocketStream) and not isinstance(xs, trio.socket.SocketType) and \
            not isinstance(xs, trio.SSLStream):
        return False
    if xs not in socket_data.mysockets:
        return False
    if socket_data.which_socket[xs] == 'cs':
        if xs not in socket_data.mynick:
            return False
    if xs not in socket_data.send_buffer:
        return False
    return True


async def aclose_both(sc_socket: trio.SocketStream | trio.SSLStream) -> None:
    """Close both irc-server and irc-client sockets together

    @param sc_socket: only one out of the two sockets is rqeuired
    @return: None
    :rtype: None

    """
    try:
        await sc_socket.aclose()
    except (trio.ClosedResourceError, trio.BrokenResourceError, gaierror, OSError):
        pass
    try:
        await socket_data.mysockets[sc_socket].aclose()
    except (trio.ClosedResourceError, trio.BrokenResourceError, gaierror, OSError, KeyError):
        pass
    return None


class EndSession(BaseException):
    """
    An BaseException to raise when paired sockets are closed.
    """

    def __init__(self, args: str | None = '', close_socket: trio.SocketStream | trio.SSLStream | None = None):
        self.args: list[str] = [str(args)]
        if close_socket is not None:
            socket_data.clear_data(close_socket)


def usable_decode(text: bytes) -> str:
    """Decode the text so it can be used.
        vars:
            :@param text: a string of bytes that needs decoding
            :@return: string of decoded bytes (text)

    """
    try:
        decoded_text: str
        decoded_text = text.decode("utf8")
    except (UnicodeWarning, EncodingWarning, UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
        try:
            decoded_text = text.decode("latin1")
        except (UnicodeWarning, EncodingWarning, UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
            try:
                det = detect(text)
                decoded_text = text.decode(det['encoding'], errors="replace")
            except (EncodingWarning, UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
                return ''
            except (UnicodeWarning,) as exp:
                pass
    return decoded_text


def get_words(text: str) -> list:
    """Returns the words list of the first line in list

        vars:
            :@param text: A string of text with lines ending in cr, lf, and crlf
            :@return: a list of words split on whitespace.

    """
    try:
        text = text.strip()
        lower_string: str = text.lower()
        while '\r' in lower_string:
            lower_string = lower_string.replace("\r", "")
        while '\f' in lower_string:
            lower_string = lower_string.replace("\f", "")
        while '\t' in lower_string:
            lower_string = lower_string.replace("\t", "")
        return lower_string.split(' ')
    except (ValueError, TypeError):
        return ['']


async def before_connect_sent_connect(cs_sent_connect: trio.SocketStream
                                                       | trio.SSLStream, byte_string: str) -> None:
    """The socket is in a state where the client has just sent the CONNECT
    protocol statement but has not received an reply yet.

        vars:
            :@param cs_sent_connect: the client socket
            :@param byte_string: string the first line received from client_socket
            :@return: Returns None

    """
    lower_words: str = byte_string.strip().lower()
    words: list[str] = get_words(lower_words)

    if len(words) < 3 or len(words) > 3:
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 Bad Request. Requires proper http/1.0 protocol.\r\n\r\n".encode()
        )
        await aclose_sockets(sockets=(cs_sent_connect,))
        return None
    if words[0] != "connect":
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 Bad Request. Proxy use only for IRC networks.\r\n\r\n".encode()
        )
        await aclose_sockets(sockets=(cs_sent_connect,))
        return None
    host: str = words[1]

    if ":" not in host:
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 Bad Request. Requires `server:port` to connect to.\r\n\r\n".encode()
        )
        await aclose_sockets(sockets=(cs_sent_connect,))
        return None
    server: str = ':'.join(host.split(":")[0:-1])
    port: str = host.split(":")[-1]
    try:
        port_num: int = int(port)
    except ValueError:
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 bad request. requires integer port number.\r\n\r\n".encode()
        )
        await aclose_sockets(sockets=(cs_sent_connect,))
        return None
    await proxy_make_irc_connection(cs_sent_connect, server, port_num)


async def proxy_make_irc_connection(client_socket: trio.SocketStream
                                                   | trio.SSLStream, ss_hostname: str, port: int) -> None:
    """Make a connection to the IRC network and fail (502) if unable to connect.
    vars:
        :type server: str
        :@param client_socket: the client socket
        :@param server: a string of the server to connect to
        :@param port: the port number to connect to (integer)
        :@return: returns None


    """
    # print("making irc connection")
    ss_hostname = ss_hostname.lower()
    server_socket: trio.SSLStream | trio.SocketStream
    server_socket_nossl: trio.SocketStream
    try:
        granted: bytes = b"HTTP/1.0 200 connection started with irc server.\r\n\r\n"
        if not await socket_data.raw_send(client_socket, None, granted):
            return None
    except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
            trio.BusyResourceError, gaierror, OSError):
        return None
    try:
        if port in (6697, 9999, 443, 6699, 6999, 7070) \
                or (port == 7000 and ss_hostname != 'irc.dal.net') and ss_hostname != 'irc.undernet.org':
            ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            try:
                server_socket: trio.SocketStream | trio.SSLStream = await trio.open_ssl_over_tcp_stream(
                                                                                        ss_hostname,
                                                                                            port,
                                                                                    https_compatible=False,
                                                                                    ssl_context=ssl_context,
                                                                                    happy_eyeballs_delay=0.180)
            except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                    trio.BusyResourceError, gaierror, OSError, trio.NoHandshakeError,
                    ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                    ConnectionError, BaseException):
                try:
                    with trio.fail_after(5.8):
                        await socket_data.raw_send(client_socket, None,
                                               b"HTTP/1.0 502 Unable to connect to remote host.\r\n\r\n")
                        await aclose_sockets(sockets=(client_socket, None))
                except (trio.TooSlowError, trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                            trio.BusyResourceError, gaierror, OSError, trio.NoHandshakeError,
                            ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                            ConnectionError, BaseException):
                    return None

        else:
            try:
                server_socket: trio.SocketStream | trio.SSLStream = \
                    await trio.open_tcp_stream(ss_hostname, port, happy_eyeballs_delay=0.180)
            except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                    trio.BusyResourceError, gaierror, OSError, trio.NoHandshakeError,
                    ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                    ConnectionError, BaseException):
                try:
                    await socket_data.raw_send(client_socket, None,
                                               b"HTTP/1.0 502 Unable to connect to remote host.\r\n\r\n")
                    await aclose_sockets(sockets=(client_socket, None))
                except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                        trio.BusyResourceError, gaierror, OSError, trio.NoHandshakeError,
                        ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                        ConnectionError, BaseException):
                    return None
        await trio.sleep(3)
        socket_data.create_data(client_socket, server_socket)
        socket_data.hostname[server_socket] = ss_hostname + ':' + str(port)

        async with trio.open_nursery() as nursery:
            # Server_socket marked by 'ss' as the last parameter, writes to cs
            nursery.start_soon(socket_received_chunk, client_socket, server_socket, 'ss')
            # client_socket marked by 'cs' as the last parameter, writes to ss
            nursery.start_soon(socket_received_chunk, client_socket, server_socket, 'cs')
            # Write to client
            nursery.start_soon(write_loop, client_socket, server_socket, socket_data.send_buffer[client_socket], 'cs')
            # Write to server
            nursery.start_soon(write_loop, client_socket, server_socket, socket_data.send_buffer[server_socket], 'ss')
    except (EndSession,):
        socket_data.clear_data(client_socket)
        await aclose_both(client_socket)
        # return
        return
    except BaseException:
        print('BaseException #001A')
        socket_data.clear_data(client_socket)
        await aclose_both(client_socket)
        return
    finally:
        # proxy_make_irc_connection()
        print("connections were closed. nursery finished.")


def exc_print(msg) -> str:
    """Removes excess brackets from exception message
    Vars:
        :@param msg: The exception message to strip extra parenthesis from
        :@return: returns string of new exception message

    """
    return str(msg).strip(str(chr(34) + chr(39) + chr(40) + chr(41) + chr(44)))


async def write_loop(client_socket: trio.SocketStream |
                                    trio.SSLStream, server_socket: trio.SocketStream | trio.SSLStream,
                     send_buffer: Deque[str | bytes | str], which_sock: str) -> None:
    """The server sockwrite write loop.

    vars:
        :@param client_socket: client socket
        :@param server_socket: server socket
        :@param send_buffer: deque of lines of text to send
        :@param which_sock: = 'cs' or 'ss' to know which to send to. a write_loop() for each socket.
        :@return: None

    """
    line: bytes = b''
    while (client_socket in socket_data.mysockets) and (server_socket in socket_data.mysockets):
        if not line:
            try:
                line = usable_decode(send_buffer.popleft()).strip().encode('utf-8', errors='replace')
            except IndexError:
                await trio.sleep(0.250)
                line = b''
                continue
            line += b"\r\n"
        with trio.fail_after(28):
            try:
                if which_sock == 'cs':
                    await client_socket.send_all(line)
                else:
                    await server_socket.send_all(line)
                line = b''
                continue
            except (trio.BusyResourceError,):
                await trio.sleep(0.120)
                continue
            except (trio.BrokenResourceError, trio.ClosedResourceError, gaierror,
                    trio.TooSlowError, OSError, BaseException) as exc:
                print('write error! ' + which_sock + ' ' + str(exc) + ' '
                      + str(exc.args) + ' LINE: ' + str(line))
                raise EndSession('Write Error. ' + which_sock + ' ' + str(line))
        await trio.sleep(0)


async def ss_updateial(client_socket: trio.SocketStream | trio.SSLStream,
                       server_socket: trio.SocketStream | trio.SSLStream,
                       single_line: str, split_line: list[str]) -> \
        bool | None:
    """The function execution chain in reverse is
    updateial...() -> ss_got_line...() then fast_line()
    there is also another one on the same path but instead
    of this function it is ss_parse_line(). Client data
    is not checked except for in the case of DCC connections.
    vars:
        :@param split_line: The split line for the incoming data lines from the irc-server
        :@param single_line: the single string line with uppercase for relay to irc-client
        :@param client_socket: trio.SocketStream | trio.SSLStream client socket
        :@param server_socket: trio.SocketStream | trio.SSLStream server socket
        :@return: bool or SNone. False if silenced or None if relayed to client.

    """
    newnick: str
    awaymsg: str
    return_silent: bool = False
    chan: str = ''
    upper_nick_src: str
    upper_nick_full_src: str
    original_line: str = single_line
    orig_upper_split: list[str] = single_line.split(' ')
    split_line: list[str, ...] = single_line.lower().split()
    nick_src: str = single_line.split(' ')[0].split('!')[0].lower()
    src_nick_full: str = single_line.split(' ')[0].lower()
    upper_nick_src: str
    upper_nick_dest: str
    old_nick: str
    source_upper: str
    source: str
    if original_line[0] == '@':
        single_line = ' '.join(single_line.split(' ')[1:])
        orig_upper_split = original_line.split(' ')[1:]
        split_line = split_line[1:]
    if '!' in split_line[0]:
        upper_nick_src: str = colourstrip(orig_upper_split[0].split('!')[0].lstrip(':'))
        upper_nick_full_src: str = colourstrip(orig_upper_split[0].lstrip(':'))
        src_nick_full = upper_nick_full_src.lower()
        nick_src = upper_nick_src.lower()
        socket_data.state[client_socket]['upper_nick'] = upper_nick_src
    if split_line[1] == "nick":
        upper_nick_dest = colourstrip(orig_upper_split[2].lstrip(':'))
        upper_nick_src = colourstrip(orig_upper_split[0].split('!')[0])
        nick_src = upper_nick_dest.lower()
        old_nick = upper_nick_src.lower()
        upper_nick_src = upper_nick_dest
        src_nick_full = colourstrip(nick_src + "!" + split_line[0].split("!")[1])
        upper_nick_full_src = colourstrip(upper_nick_src + '!' + orig_upper_split[0].lower().split('!')[1])
        if old_nick == socket_data.mynick[client_socket]:
            socket_data.mynick[client_socket] = nick_src
            socket_data.state[client_socket]['upper_nick'] = upper_nick_dest
            socket_data.set_face_nicknet(client_socket)
        ial.IALData.ial_add_newnick(client_socket, old_nick, nick_src, src_nick_full)
        return None
    if len(split_line) < 2:
        return None
    if chan:
        chan = chan.lstrip(':')
    if single_line[0] == ':':
        source_upper = single_line.split(' ')[0]
        source = source_upper.lower()
        single_line = ' '.join(single_line.split(' ')[1:])
        orig_upper_split = original_line.split(' ')[1:]
    if split_line[0] == 'mode':
        return None
    if split_line[0] == "part":
        chan = split_line[1].lstrip(':')
        chan = chan.lower()
        print(F"PARTING CHANNEL {chan}")
        if nick_src == socket_data.mynick[client_socket]:
            socket_data.mychans[client_socket].discard(chan)
            ial.IALData.ial_remove_chan(client_socket, chan)
        else:
            ial.IALData.ial_remove_nick(client_socket, nick_src, chan)
            ial.IALData.myial_count[client_socket][chan] -= 1
    if split_line[0] == "join":
        chan = orig_upper_split[1].lower()
        chan = chan.lstrip(':')
        my_usernick = socket_data.mynick[client_socket]
        if nick_src != my_usernick:
            if client_socket not in ial.IALData.myial_count:
                ial.IALData.myial_count[client_socket] = {}
            if chan not in ial.IALData.myial_count[client_socket]:
                ial.IALData.myial_count[client_socket][chan] = 1
            ial.IALData.myial_count[client_socket][chan] += 1
        ial.IALData.ial_add_nick(client_socket, nick_src, src_nick_full, chan)
        if nick_src == my_usernick:
            socket_data.mychans[client_socket].add(chan)
            if client_socket not in ial.IALData.who:
                ial.IALData.who[client_socket] = {}
            ial.IALData.who[client_socket][chan] = '0'
            if client_socket not in ial.IALData.myial_count:
                ial.IALData.myial_count[client_socket] = {}
            ial.IALData.myial_count[client_socket][chan] = 0
    if split_line[0] == "352":
        # /who list
        nick = colourstrip(split_line[7].lower())
        addr = colourstrip(split_line[5].lower())
        identd = colourstrip(split_line[4].lower())
        fulladdr = nick + "!" + identd + "@" + addr
        chan = split_line[2].lower()
        if chan[0] != "#":
            return None
        if chan not in socket_data.mychans[client_socket]:
            return None
        ial.IALData.ial_add_nick(client_socket, nick, fulladdr, chan=chan)
        if ial.IALData.who[client_socket][chan] == '0':
            ial.IALData.who[client_socket][chan] = 'inwho'
        if ial.IALData.who[client_socket][chan] == 'inwho':
            return False
        return None
    if split_line[0] == "315":
        chan = split_line[2].lower()
        if chan[0] != '#':
            return None
        if ial.IALData.who[client_socket][chan] == 'inwho':
            ial.IALData.who[client_socket][chan] = '1'
            return False
        return None
    if split_line[0] == "353":
        # /names
        # print('Error With: '+single_line)
        if len(split_line) < 5:
            return None
        nicks: list[str, ...]
        nicks = [split_line[4].lstrip(':')]
        print(f'nicks: {nicks}')
        print('remove full colon!')
        if len(split_line) > 5:
            nicks += split_line[5:]
        chan = split_line[3]
        ial.IALData.myial_count[client_socket][chan] += len(nicks)
    if split_line[0] == "366":
        # End of /names
        chan = split_line[2]
        if ial.IALData.ial_count_nicks(client_socket, chan) == \
                ial.IALData.myial_count[client_socket][chan]:
            return None
        th = Timer(randint(3, 12), lambda: ial.IALData.sendwho(server_socket, th, chan))
        ial.IALData.timers.add(th)
        th.start()
    if split_line[0] == '336':
        pass
    if split_line[0] == '322':
        # print('add chan')
        # /List channel usrs :topic
        pass
    if split_line[0] == '323':
        print('done list')
        # /List ENd of List
    if split_line[0] == '321':
        print('start list')
        # /List starting list
    if split_line[0] == 'away':
        try:
            awaymsg: str = ' '.join(single_line.split(' ')[1:])
        except IndexError:
            awaymsg: str = ''
        finally:
            cs_away_msg_notify(client_socket, nick_src, awaymsg)

    if split_line[0] == "privmsg":
        chan = split_line[1]
        if chan[0] != '#':
            chan = ''
        # if nick in socket_data.myial[client_socket]:
        # return_silent = ial.IALData.ial_add_nick(client_socket, nick, nick_src)
    if return_silent is True:
        return False
    return None


def cs_away_msg_notify(client_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Notify the client that the user is away when joining the channel or talking in the channel

    :@param client_socket: the socket to the irc-client
    :@param nick: the string nickname that is set-away
    :@param msg: the string away-message, if any
    :@return: None

    """
    if not nick:
        return None
    msg = msg.lstrip(': \t\f')
    msg = msg.rstrip('\t\f\r\n ')
    away = "\x02Away:\x02" + msg
    back = "\x02Back\x02"
    if not msg:
        parm = back
    else:
        parm = away
    cs_send_notice(client_socket, "User " + nick + " is set " + parm)
    return None


def lower_strip(text: str) -> str:
    """lower text, strip text, mirc colour removal
    :@param text: text to be stripped, lowered, and removed colour; to be parsed.
    :@return: returns the string

    """
    text = text.lower()
    text = text.strip()
    text = colourstrip(text)
    return text


async def socket_received_chunk(client_socket: trio.SocketStream | trio.SSLStream,
                                server_socket: trio.SocketStream | trio.SSLStream, which_sock) -> bool | None:
    """Read loop to receive data from the socket and pass it to
        fast_line_split_for_read_loop()

        :@param client_socket: client socket stream
        :@param server_socket: irc server socket stream
        :@return: returns if the nursery needs to be closed.
    """

    if 'connecting' == socket_data.state[client_socket]['doing']:
        socket_data.state[client_socket]['doing'] = 'signing on'
        socket_data.echo(client_socket, 'connected to ' + socket_data.hostname[server_socket])

    if which_sock == 'ss':
        rcvd_line = ss_received_line
        dest_socket = server_socket
    else:
        rcvd_line = cs_received_line
        dest_socket = client_socket

    read_line: bytes = b''
    read_str: str = ''
    read_strip: str = ''
    read_split: list[None | str, ...] = []
    read_some: bytes
    find_n: int = -1
    read_sock: bytes = b''
    while True:
        try:
            read_sock = await dest_socket.receive_some(32100)
        except trio.BusyResourceError:
            await trio.sleep(0.100)
            continue
        except trio.BrokenResourceError:
            raise EndSession('irc server forcefully closed the connection')
        if read_sock == b'':
            raise EndSession('Connection closed')
        read_line += read_sock
        while True:
            find_n = read_line.find(b'\n')
            if find_n == -1:
                break
            read_some_found: int = find_n + 1
            read_some = read_line[0:find_n + 1]
            # print(b'read some: ' + read_some)
            read_str = usable_decode(read_some)
            read_str = read_str.strip()
            read_strip = lower_strip(read_str)
            read_split = read_strip.split(' ')
            await rcvd_line(client_socket, server_socket, read_str, read_split)
            remain = read_line[read_some_found:]
            read_line = remain
            # print(b'remaining: ' + read_line)
        if find_n == -1:
            read_str = ''
            read_strip = ''
            read_split = []
            read_sock = b''
            find_n = -1
        await trio.sleep(0.225)


async def ss_received_line(client_socket: trio.SocketStream | trio.SSLStream,
                           server_socket: trio.SocketStream | trio.SSLStream, single_line: str,
                           split_line: list[str, ...]) -> None:
    """Received a complete line of text and process here

        @param client_socket: socket to the irc-client
        @param server_socket: socket to te irc-server
        @param single_line: single line of upper-case string to send the server or client
        @param split_line: list of split lines on \n and lowered and stripped of colour
        @return: None

    """

    # from above ss_received_chunk()
    dest_socket: trio.SocketStream | trio.SSLStream = client_socket
    nick_src: str = ''
    original_line: str = single_line
    single_line = single_line.lower()
    # actions.sc_send(dest_socket, original_line)
    if len(split_line) == 0:
        actions.sc_send('\r\n')
        return

    if check_mirc_exploit(original_line) is True:
        await exploit_triggered(client_socket, server_socket)
        await trio.sleep(0)
        return None
    if original_line[0] == '@':
        if not single_line.startswith('@time') and not single_line.startswith('@account') and not \
                single_line.startswith('@batch'):
            print('Line starts with a new @ sign text')
            print('@@@@@@ @@@ @ @ ' + original_line)
            await trio.sleep(0)
        del split_line[0]
        single_line = ' '.join(split_line)
        orig_upper_split = original_line.split(' ')[1:]
    else:
        orig_upper_split = original_line.split(' ')

    ial_send = await ss_updateial(client_socket, server_socket, single_line, orig_upper_split)
    if ial_send is False:
        await trio.sleep(0)
        return None
    source_line: str
    if single_line[0] == ':':
        source_line = split_line[0]
        del split_line[0]
        single_line = ' '.join(split_line)

    if '!' in orig_upper_split[0]:
        upper_nick_src = orig_upper_split[0].split('!')[0].lstrip(':')
        nick_src = upper_nick_src.lower()

    if len(split_line) == 1:
        actions.sc_send(dest_socket, original_line)
        await trio.sleep(0)
        return None

    if split_line[0] == '375':
        # motd start 3rd param is nickname
        if socket_data.state[client_socket]['motd_def']:
            send_motd(dest_socket, split_line[1])
            await trio.sleep(0)
            return None

    if split_line[0] == '372':
        # motd msg
        if socket_data.state[client_socket]['motd_def']:
            await trio.sleep(0)
            return None

    if split_line[0] == '376' or split_line[0] == "422":
        # End of /motd # keep track if it is the first motd (on connect) or already connected.
        # Keep track of neither 376 nor 422 is used.
        if not socket_data.state[client_socket]['connected']:
            socket_data.state[client_socket]['doing'] = 'signed on'
            socket_data.state[client_socket]['connected'] = time()
    if split_line[0] == '376':
        # End of /motd
        if socket_data.state[client_socket]['motd_def']:
            socket_data.state[client_socket]['motd_def'] = 0
            await trio.sleep(0)
            return None
    elif split_line[0] == '005':
        sock_005(client_socket, original_line)
        await trio.sleep(0)
    elif split_line[0] in ("001", "372", "005", "376", "375", "422"):
        socket_data.state[client_socket]['doing'] = 'signed on'
        socket_data.mynick[client_socket] = split_line[2].lower()
        socket_data.state[client_socket]['upper_nick'] = orig_upper_split[2]
        socket_data.set_face_nicknet(client_socket)
        await trio.sleep(0)
    elif split_line[0] == '301':
        reason = " ".join(orig_upper_split[4:]).strip(':\r\n ')
        msg = f":www.mslscript.com NOTICE {socket_data.mynick[client_socket]}" \
              f" :User {orig_upper_split[3]} is" \
              f" set away, reason: {reason}"
        actions.sc_send(client_socket, msg)

    actions.sc_send(client_socket, original_line)
    await trio.sleep(0)
    return None


async def cs_received_line(client_socket: trio.SocketStream | trio.SSLStream,
                           server_socket: trio.SocketStream | trio.SSLStream,
                           single_line: str, split_line: list[str]) -> None:
    """Client socket received a line of data.
            Vars:
                :@param client_socket: client socket
                :@param server_socket: server socket
                :@param single_line: string of words
                :@param split_line: single_line split on words
                :@return: None

    """
    dest_socket = server_socket
    # if single_line == '':
    #     actions.sc_send(server_socket, '\n')
    #     return
    original_line = single_line
    single_line = single_line.lower()
    split_line_low: list[str, ...] = single_line.split(' ')
    split_line: list[str, ...] = original_line.split(' ')
    print(original_line)
    if split_line_low[0] == 'nick' and len(split_line) == 2:
        socket_data.mynick[client_socket] = split_line[1].lstrip(':')

    if split_line_low[0] == 'names':
        chan = split_line_low[1].lstrip(':')
        ial.IALData.myial_count[client_socket][chan] = 0
        actions.sc_send(dest_socket, original_line)
        await trio.sleep(0)
        return

    len_split_line: int = len(split_line)
    if len_split_line < 2:
        actions.sc_send(dest_socket, original_line)
        await trio.sleep(0)
        return None
    halt_on_yes: bool | None = False
    if split_line_low[1].startswith('trio') or split_line_low[1].startswith('proxy') or \
            split_line_low[1].startswith('xdcc') or split_line_low[1].startswith('py'):
        halt_on_yes = cs_rcvd_command(client_socket, server_socket, original_line, split_line_low)
    if not halt_on_yes:
        actions.sc_send(dest_socket, original_line)
    await trio.sleep(0)
    return None


def sock_005(client_socket: trio.SocketStream | trio.SSLStream, single_line: str) -> None:
    """Parses the 005 numeric from the irc-server

    :@param client_socket: the socket to the irc-client
    :@param single_line: a single line of text read from a socket
    :@return: None
    """
    upper_line_str: str = single_line.strip()
    upper_line: list[str] = upper_line_str.split(' ')
    if upper_line_str[0] == ':':
        upper_line = upper_line[3:]
    else:
        upper_line = upper_line[2:]
    key: str
    value: str | int
    if not upper_line:
        return None
    for name in upper_line:
        if name[0] == ":":
            break
        if "=" in name:
            key = name.split("=")[0]
            value = name.split("=")[1]
        else:
            key = name
            value = name
        if value.isdigit():
            value = int(value)
        key = key.lower()
        socket_data.raw_005[client_socket][key] = value
    socket_data.set_face_nicknet(client_socket)
    return None


def dur_replace(in_words: str) -> str:
    """Shorten the time duration text

    @param in_words: The words of the time duration string
    @return: string
    """
    in_words = in_words.replace('week', 'wks')
    in_words = in_words.replace('day', 'dys')
    in_words = in_words.replace('hour', 'hrs')
    in_words = in_words.replace('minute', 'mins')
    in_words = in_words.replace('second', 'secs')
    in_words = in_words.replace('ss', 's')
    return in_words


def send_motd(client_socket: trio.SocketStream | trio.SSLStream, mynick: str) -> None:
    """The replaced MOTD sent to the irc-client upon connecting

    @param client_socket: the socket to the irc-client
    @param mynick: the string of irc-client nickname to send the MOTD to
    @return: None

    """
    prefix = ':www.mslscript.com 375 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + 'www.mslscript.com Message of the Day -')
    prefix = ':www.mslscript.com 372 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + '\x02replacing MOTD\x02 -')
    actions.sc_send(client_socket, prefix.strip())
    actions.sc_send(client_socket, prefix + 'To connect to a SSL port, '
                                            '\x02DO NOT\x02 prefix the port with -')
    actions.sc_send(client_socket, prefix + 'a \x02+\x02 character. End-to-end encryption'
                                            ' is not possible; but SSL from proxy to irc server is. -')
    actions.sc_send(client_socket, prefix + 'Trio-ircproxy.py \x02will\x02 use SSL for '
                                            'irc -')
    actions.sc_send(client_socket, prefix + 'server connections on specific ports. -')
    actions.sc_send(client_socket, prefix)
    actions.sc_send(client_socket, prefix + 'Type \x02/proxy-commands\x02 for list of valid '
                                            'commands. -')
    actions.sc_send(client_socket, prefix + 'Type \x02/xdcc-commands\x02 for list of xdcc '
                                            'commands. -')
    actions.sc_send(client_socket, prefix + "Type \x02/proxy-help\x02 for first use "
                                            "instructions. -")
    actions.sc_send(client_socket, prefix)
    actions.sc_send(client_socket, prefix + "To view the irc server's MOTD type "
                                            "\x02/motd\x02 -")
    actions.sc_send(client_socket, prefix + "Trio-ircproxy.py and Machine-Gun mSL script"
                                            " official website: -")
    actions.sc_send(client_socket, prefix + "Server: \x1fhttps://www.mslscript.com/index.html\x1f -")
    actions.sc_send(client_socket, prefix + "'X-Clacks-Overhead':\x02 'GNU Terry Pratchett' \x02-")
    prefix = ':www.mslscript.com 376 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + 'End of /MOTD -')
    return None


time_last_pong: float = 0.0


def cs_rcvd_command(client_socket: trio.SocketStream | trio.SSLStream,
                    server_socket: trio.SocketStream | trio.SSLStream,
                    single_line: str, split_line: list[str]) -> bool | None:
    """Received a command from the irc-client

    @param client_socket: socket to irc-client
    @param server_socket: socket to irc-server
    @param single_line: single line string of text
    @param split_line: single_line split on words
    @return: bool of True to not relay to irc-server or None to relay to irc-server

    """
    return None
    del split_line[0]

    if len(split_line) >= 2 and split_line[0] == '.colour':
        actions.sc_send(client_socket,
                        ':ashburry!mg-script@www.mslscript.com privmsg ashburry :colour is: ' + str(
                            ord(split_line[1][0]))
                        + ' = ' + split_line[1][0])
        # yes_halt = True to NOT send to server
        return True

    if 'xdcc' in split_line[0]:
        xdcc_system.xdcc_commands(client_socket, server_socket, single_line, split_line)
        return True
    if 'trio' in split_line[0] or 'proxy' in split_line[0]:
        proxy_commands.commands(client_socket, server_socket, single_line, split_line)
        return True
    from url_desc.url_desc import get_url_desc
    if (split_line[0] == '.url') and (len(split_line) == 2):
        chan = single_line.split(' ')[1]
        url, title, desc = get_url_desc(split_line[1].lstrip(':'))
        chan = chan
        actions.sc_send(server_socket, f'privmsg {chan} :URL: {url}')
        actions.sc_send(server_socket, f'privmsg {chan} :Title: {title}')
        actions.sc_send(server_socket, f'privmsg {chan} :Description: {desc}')
    return None


def verify_login(auth_userlogin: str) -> bool | tuple[str, str]:
    """Validate user: pass login attempt

        :@param auth_userlogin: The `user: pass` login attempt
        :@return: bool True of ok False if not-ok

    """
    auth_pass: str = ''
    auth_user: str = ''
    try:
        auth_login: str = usable_decode(b64decode(auth_userlogin))
        print(auth_login)
        auth_pass = auth_login[auth_login.find(":") + 1:]
        auth_user = auth_login[:auth_login.find(":")]
        auth_user = auth_user.strip()
        auth_user = auth_user.lower()
        print('### PASS ' + auth_pass)
        print('### USER ' + auth_user)
        if not auth_pass or not auth_user or len(auth_user) > 50 or len(auth_pass) > 40:
            return False
        if auth_login.count(":") > 1 or auth_login.count(':') < 1 or auth_login.count(" ") > 1 \
                or verify_user_pwdfile(auth_user, auth_pass) is False:
            print('BAD PASSWORD / BAD PASSWORD / BAD PASSWORD')
            return False
        return (auth_user, auth_pass)
    except ValueError:
        print('BAD PASSWORD / BAD PASSWORD / BAD PASSWORD')
        return False
    finally:
        auth_pass = "a" * len(auth_pass)
        auth_user = "a" * len(auth_user)
        del auth_pass
        del auth_user


async def authenticate_proxy(client_socket: trio.SocketStream, auth_lines: list[str]) -> bool | tuple[str, str]:
    """Check for bad login attverify_userempt
        parameters:

        :client_socket: client socket
        :auth_lines: the remaining lines of text after the first line

    """
    i = 0
    while True:
        if i > (len(auth_lines) - 1) or len(auth_lines) == 0:
            socket_data.echo(client_socket, "Missing authentication attempt.")
            with trio.move_on_after(18):
                await client_socket.send_all(b"407 Proxy authentication required.\r\n")
                await client_socket.send_all(
                    b'WWW-Authenticate: Basic realm="trio-ircproxy user realm", \
                                    charset="UTF-8"\r\n\r\n'
                )
            await client_socket.aclose()
            return False
        auth: str = auth_lines[i].lower()
        if "authorization:basic" in auth:
            auth = auth.replace(":", ": ")
        while '  ' in auth:
            auth = auth.replace("  ", " ")
        auth = auth.split(" ")[0]
        if auth not in ("authorization:", "proxy-authorization:"):
            i += 1
            continue
        break

    auth_words: str = auth_lines[i]
    auth_words = auth_words.replace(":", ": ")
    while "  " in auth_words:
        auth_words = auth_words.replace("  ", " ").strip()
    auth_words_split: list[str] = auth_words.split(" ")
    auth_words_split = auth_words_split[1:]
    if len(auth_words_split) != 2:
        with trio.move_on_after(18):
            socket_data.echo(client_socket, "Disconnected, missing username/password "
                                            "attempt.")
            await client_socket.send_all(b"407 You need an login to continue.\r\n\r\n")
            await client_socket.send_all(
                b'WWW-Authenticate: Basic realm="trio-ircproxy user'
                + b' realm", charset="UTF-8"\r\n\r\n'
            )
        await client_socket.aclose()
        return False
    if auth_words_split[0].lower() != "basic":
        socket_data.echo(client_socket, "Disconnected, invalid authentication type attempt.")
        with trio.move_on_after(18):
            await client_socket.send_all(b"407 you need Basic authentication type.\r\n\r\n")
            await client_socket.send_all(
                b'WWW-Authenticate: Basic realm="trio-ircproxy user'
                + b' realm", charset="UTF-8"\r\n\r\n'
            )
        await client_socket.aclose()
        return False
    name: bool | tuple[str, str] = verify_login(auth_words_split[1])
    if not name:
        socket_data.echo(client_socket, "Disconnected, bad username/password attempt.")
        with trio.move_on_after(15) as cancel_scope:
            await client_socket.send_all(b"401 Unauthorized. Bad username/password"
                                         + b" attempt.\r\n\r\n")
        raise EndSession('bad username/password', client_socket)
    return name


def check_fry_server(ip_addy: tuple | list | str) -> bool:
    """Makes sure the server is not being hammered
    by a specific IP address. Checks after 20 connections.
    If you plan on using the Proxy Server in a hammering fasion
    you can add an IP to the immune list see "/raw proxy-help immune"

    :@param ip_addy: a tuple, list or string of an IP address
    :@return: True if IP is okay or False if the IP needs to be blocked.
    """

    if isinstance(ip_addy, (tuple, list)):
        ip_addy: str = ip_addy[0]
    if ip_addy in system_data.FryServer_json["immune"]:
        return True

    # int, number of connections
    max_cons: int = int(system_data.FryServer_json["settings"]['max_reconnections'])
    # int, within seconds of each other
    max_time: int = int(system_data.FryServer_json["settings"]["max_time"])
    new_time: str = str(int(time()))
    for old_ip in list(system_data.FryServer_json["ip_list"]):
        old_check: str = system_data.FryServer_json["ip_list"][old_ip]
        old_check_split: list[str] = old_check.split(" ")
        if len(old_check_split) != 2:
            del system_data.FryServer_json["ip_list"][old_ip]
            continue
        if int(new_time) - int(old_check_split[1]) >= max_time:
            del system_data.FryServer_json["ip_list"][old_ip]

    old_check: str = system_data.FryServer_json["ip_list"].get(ip_addy, "0 " + new_time)
    old_check_split: list[str] = old_check.split(" ")
    system_data.FryServer_json["ip_list"][ip_addy] = (
            str(int(old_check_split[0]) + 1) + " " + old_check_split[1]
    )
    if int(new_time) - int(old_check_split[1]) < max_time:
        system_data.FryServer_json["ip_list"][ip_addy] = (
                str(int(old_check_split[0]) + 1) + " " + new_time
        )
        if int(old_check_split[0]) + 1 >= max_cons:
            return False

    return True


async def proxy_server_handler(cs_before_connect: trio.SocketStream) -> None:
    """Handle a connection to the proxy server.
                        Accept proxy http/1.0 protocol.
        vars:
        :@param cs_before_connect: the live socket already accepted and
                        ready for reading (1 byte at a time).
        :@return: None
    """
    # Write down tries per minute for this IP. And just close them all if its too many.
    try:
        hostname: str = cs_before_connect.socket.getpeername()[0]
    except socket.gaierror:
        hostname = 'unknown'
    print(hostname)
    if not check_fry_server(hostname):
        socket_data.clear_data(cs_before_connect)
        await aclose_sockets(sockets=(cs_before_connect,))
        print(':::::: FRY_SERVER TRIGGERED ::::::')
        return None
    socket_data.hostname[cs_before_connect] = hostname
    port = f'{cs_before_connect.socket.getsockname()[1]}'
    socket_data.echo(cs_before_connect, "Accepted a client connection " + hostname + " on port " + str(port) + '...')
    bytes_data: bytes
    byte_string: str = ""
    auth: bool | None | tuple[str, str]
    while True:
        try:
            bytes_data: bytes
            with trio.move_on_after(35) as cancel_scope:
                bytes_data: bytes = await cs_before_connect.receive_some(1)
            if cancel_scope.cancelled_caught:
                # proxy_server_handler
                socket_data.clear_data(cs_before_connect)
                await aclose_sockets(sockets=(cs_before_connect,))
                socket_data.echo(cs_before_connect, "Server is too slow to send data. Socket closed.")
                raise EndSession('Client closed connection. Make sure your client is set to use Proxy not SOCKS.')
            byte_string += usable_decode(bytes_data)
            if not byte_string.endswith("\r\n\r\n"):
                continue
            break
        except (BaseException, EndSession, trio.Cancelled, trio.BrokenResourceError,
                trio.ClosedResourceError, trio.BusyResourceError, trio.TrioInternalError) as exc:
            print("handler EXCEPT 1: " + str(exc.args))
            await aclose_both(cs_before_connect)
            socket_data.clear_data(cs_before_connect)
            await trio.sleep(0)
            raise
    try:
        auth: bool | tuple[str, str]
        byte_string = byte_string.strip()
        byte_string = byte_string.replace("\r", "\n")
        while "\n\n" in byte_string:
            byte_string = byte_string.replace("\n\n", "\n")
        while "  " in byte_string:
            byte_string = byte_string.replace("  ", " ")
        lines: list[str] = byte_string.split("\n")
        while '' in lines:
            lines.remove('')
        line_no: int = 0
        for line in lines:
            lines[line_no] = line.strip()
            line_no += 1
        if len(lines) > 1:
            auth_list: list[str] = lines[1:]
            auth = await authenticate_proxy(cs_before_connect, auth_list)
        if not auth:
            return None
        print("-----------------------\n")
        print(f'AUTH={str(auth)}')
        socket_data.login[cs_before_connect] = auth[0]
        if cs_before_connect not in socket_data.state:
            socket_data.state[cs_before_connect] = {}
            socket_data.state[cs_before_connect]['doing'] = "connecting"
            if 'by_username' not in system_data.user_settings:
                system_data.user_settings['by_username'] = {}
            if auth[0] not in system_data.user_settings['by_username']:
                system_data.user_settings['by_username'][auth[0]] = set()
            system_data.user_settings['by_username'][auth[0]].add(cs_before_connect)

        async with trio.open_nursery() as sent_connect_nursery:
            sent_connect_nursery.start_soon(before_connect_sent_connect, cs_before_connect, lines[0])

    except EndSession as exc:
        print("handler EXCEPT 3: " + str(exc.args))
        await aclose_both(cs_before_connect)
        socket_data.clear_data(cs_before_connect)

    except trio.ClosedResourceError:
        await aclose_both(cs_before_connect)
        socket_data.clear_data(cs_before_connect)
    except (BaseException) as exc:
        print("handler EXCEPT 2: " + str(exc.args))
        await aclose_both(cs_before_connect)
        socket_data.clear_data(cs_before_connect)
        raise
        # this is proxy_server_handler()


async def start_proxy_listener():
    """Start the proxy server.

    """

    if Settings_ini.has_section('settings') is False:
        Settings_ini.add_section('settings')

    listen_ports: str = system_data.Settings_ini["settings"].get("listen_ports", '4321')
    print('-+')
    try:
        async with trio.open_nursery() as nursery:
            for f in listen_ports.split(' '):
                nursery.start_soon(trio.serve_tcp, proxy_server_handler, int(f))
                print("proxy is ready, listening on port " + str(f))
            print("press Ctrl+C to quit...\n")
    except (EndSession, BaseException, BaseExceptionGroup, Exception,
            KeyboardInterrupt, OSError, gaierror) as exc:
        if len(exc.args) > 1 and (exc.args[0] == 98 or exc.args[0] == 10048):
            print(
                '\nERROR: The listening port is being used somewhere else. '
                + 'Maybe trio-ircproxy.py is already running somewhere?')
        else:
            # Create a new list to to prevent modifying while looping
            await quit_all()
        print("EXC: " + str(exc.args))
        print("\nTrio-ircproxy.py has Quit! -- good-bye bear ʕ•ᴥ•ʔ\n")
        raise
        # try:
        #    sys.exit(13)
        # except SystemExit:
        #    os._exit(130)


async def quit_all() -> None:
    """send quitmsg and close all sockets.

    """
    sockets = socket_data.mysockets
    for sock in sockets:
        try:
            await actions.send_quit(sock)
        except (trio.Cancelled, trio.ClosedResourceError, trio.BrokenResourceError,
                trio.TrioInternalError, Exception, EndSession, ExceptionGroup, BaseExceptionGroup):
            pass
    return None


def begin_server() -> None:
    """Start the trio_ircproxy.py proxy server

    """
    system_data.make_settings()
    system_data.make_fryfile()
    system_data.make_nickhistory()
    system_data.make_xdcc_chan_chat()
    trio.run(start_proxy_listener)
    return None


if __name__ == "__main__":
    begin_server()
