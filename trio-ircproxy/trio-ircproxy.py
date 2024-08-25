
#!/usr/bin/python#!/usr/bin/python
# -*- coding: utf-8 -*-


# Windows:
#    "install.bat -3.11"  -+-+- (just once, forever. Use your highest installed python version)
#    "runproxy.bat"
#        or just; after you have run installed.bat:
#    "runproxy.bat"
#
#
# use the install.bat -3.13 if you are on windows with Python 3.13 installed.
# FYI: `install.bat` sets up the python3.xx virtual-environment
# and installs pip, upgrades pip and wheell, and installs requirements.txt.
# You also have runproxy.bat which is a shortcut to .\trio-ircproxy\venv\Scripts\activate.bat and then
#  "python.exe .\trio-ircproxy\trio-ircproxy.py"
#  Note: runrpoxy.bat works on Windows CMD.exe, command.com, and maybe Powershell.exe
#  (bug and implementation testing is needed continually for powershell to work.)
#
#
# Linux:
#    cd ~/Ircproxy
#    chmod +x ./install.sh
#    chmod +x ./runproxy.sh
#    python -V
#    source ./install.sh -3.12.5
#   Then everytime after this one-time installation:
#   source ./runproxy.sh



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
from scripts.trio_ircproxy.url_desc.url_desc import get_url_desc
from scripts.trio_ircproxy import actions
from scripts.trio_ircproxy import ial
from scripts.trio_ircproxy import proxy_commands
from scripts.trio_ircproxy import xdcc_system
from scripts.website_and_proxy import Settings_ini
from scripts.website_and_proxy.socket_data import SocketData as socket_data
from scripts.website_and_proxy.socket_data import aclose_sockets
from scripts.website_and_proxy.system_data import SystemData as system_data
from scripts.website_and_proxy.users import validate_login, verify_user_pwdfile
from sys import excepthook
from sys import exc_info
from socket import gaierror
from socket import error
from sys import argv
from threading import Timer
from time import time as ctime
from typing import Deque, Any, Coroutine
from chardet import detect
import sys
import os
from cryptography.fernet import Fernet
_dir = path.dirname(path.abspath(__file__))
chdir(realpath(dirname(expanduser(argv[0]))))

VERSION_NUM = "3.0.1"
WWW_SHORT_URL = 'www.MyProxyIP.com'
WWW_LONG_URL = 'https://wwww.MyProxyIP.com/'
NAKED_URL = "MyProxyIP.com"

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
    socket_data.echo(client_socket, 'There was a exploit attempt by IRC server.')
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
    proto_split: list[str] = proto.split(' ')
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
    if not isinstance(xs, trio.SocketStream) and \
            not isinstance(xs, trio.SSLStream):
        return False
    if xs not in socket_data.mysockets:
        return False
    return True


async def aclose_both(sc_socket: trio.SocketStream | trio.SSLStream) -> None:
    """Close both irc-server and irc-client sockets together

    :@param sc_socket: only one out of the two sockets is required. Can be normal or SSL, client-proxy or irc-server.
    :return: None
    :rtype: None

    """
    await actions.send_quit(sc_socket)
    return None

class EndSession(BaseException):
    """
    An BaseException to raise when paired sockets are closed.
    """

def usable_decode(text: bytes) -> str:
    """Decode the text so it can be used.
        vars:
            :@param text: a string of bytes that needs decoding
            :@return: the string of decoded bytes (str)

    """
    try:
        if text == b'':
            return ''
        decoded_text: str
        decoded_text = text.decode("latin1")
    except (UnicodeWarning, EncodingWarning, UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
        try:
            decoded_text = text.decode("utf-8")
        except (UnicodeWarning, EncodingWarning, UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
            # detect encoding:
            det = detect(text)
            return text.decode(det['encoding'], errors="replace")


    return decoded_text

def handle_newline(text: str) -> str:
    while '\r' in text:
        text = text.replace("\r", "")
    while '\f' in text:
        text = text.replace("\f", "")
    while '\t' in text:
        text = text.replace("\t", "")
    while '\n' in text:
        text = text.replace("\n", "")
    return text

def get_words(text: str) -> list:
    """Returns the words list of the first line in list

        vars:
            :text: A string of text with lines ending in cr, lf, and crlf
            :returns: a list of words split on whitespaces

    """
    text = text.strip()
    lower_string: str = text.lower()
    lower_string = handle_newline(lower_string)
    return lower_string.split(' ')


identd_list: list[list[str]] = []
async def identd_handler(server_socket: trio.SocketStream) -> None:
    print('Identd Server Connection in Progress...')
    global identd_list
    status: str = ''
    identd_one: str = ''
    identd_copied: list[str] = []

    while True:

        try:
            identd_copied: list[str] = identd_list.pop()
            identd_one = identd_copied[0]
        except IndexError:
            await trio.sleep(0.350)
            return None
        if identd_copied[1] > ctime + 60 * 3:
            continue
        break
    await trio.sleep(0)
    s: trio.SocketStream
    try:
        s = await trio.open_tcp_stream(identd_one, 114, happy_eyeballs_delay=0.10)
        print('Connected to client identd server on ' + identd_one)
        status = 'connection'
    except (BaseException, BaseExceptionGroup):
        print('NO identd running on ' + identd_one)
        status = 'no_connection'
    with trio.CancelScope() as scope:
        async with trio.open_nursery() as nursery:
            try:
                nursery.start_soon(send_identd_server, server_socket, s, status, scope)
                if status == 'connection':
                    nursery.start_soon(send_identd_client, server_socket, s)
                nursery.start_soon(identd_expire_both, server_socket, s)
            except (BaseException, BaseExceptionGroup):
                scope.cancel()
    return None


async def identd_expire_both(server_socket: trio.SocketStream, s: trio.SocketStream) -> None:
    try:
        await trio.sleep(150)
    except (BaseException, BaseExceptionGroup, Exception, ExceptionGroup):
        pass
    finally:
        await identd_expired(server_socket, s)
    return None


async def identd_expired(server_socket, s) -> None:
    try:
        await s.aclose()
    except (BaseException, BaseExceptionGroup, Exception, ExceptionGroup):
        pass
    try:
        await server_socket.aclose()
    except (BaseException, BaseExceptionGroup, Exception, ExceptionGroup):
        pass
    await trio.sleep(0)
    return None


async def send_identd_server(server_socket, s, status, scope) -> None:
    server_read_all = b''
    try:
        await trio.sleep(1)
        async for data in server_socket:
            server_read = data
            print(f"server: {data!r}")
            if status == 'no_connection':
                server_read_all += server_read
                if server_read_all.endswith(b'\n'):
                    await server_socket.send_all(server_read_all.strip() + b' : USERID : UNIX : MyProxyIP\r\n')
                    server_read_all = b''
                    break
            if status == 'connection':
                await s.send_all(server_read)
                if server_read.endswith(b'\n'):
                    break
    except (BaseException, BaseExceptionGroup, Exception, ExceptionGroup):
        await trio.sleep(0)
        raise
    scope.cancel()
    return None

async def send_identd_client(server_socket, s) -> None:
    try:
        await trio.sleep(1.390)
        async for data in s:
            print(f"client: {data!r}")
            await server_socket.send_all(data)
            if data.endswith('\n'):
                break
    except (BaseException, BaseExceptionGroup, Exception, ExceptionGroup):
        await trio.sleep(0)
    return None


async def proxy_make_irc_connection(client_socket: trio.SocketStream
                                                   | trio.SSLStream, ss_hostname: str, port: int) -> None:
    """Make a connection to the IRC network and fail (502) if unable to connect.
    vars:
        :param client_socket: the client socket holding the connection to the IRC client
        :param ss_hostname: a string of the server hostname or IP to connect to
        :param port: the port number to connect to (digit)
        :return: returns None

    """
    server_socket: trio.SSLStream | trio.SocketStream
    try:
        granted: bytes = b"HTTP/1.0 200 connection started with irc server.\r\n\r\n"
        if not await socket_data.raw_send(client_socket, None, granted):
            await aclose_sockets(client_socket)
            return None
    except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
            trio.BusyResourceError, gaierror, OSError):
        await aclose_sockets(client_socket)
        return None
    if (port == 7000 and fnmatch(ss_hostname, '*.dal.net') == True):
        server_socket = await make_normal_socket(client_socket, ss_hostname, port)
    elif fnmatch(ss_hostname, '*.undernet.org') == True:
        server_socket = await make_normal_socket(client_socket, ss_hostname, port)
    elif port in (6697, 9999, 443, 6699, 6999, 7070, 7000):
        server_socket = await make_SSL_socket(client_socket, ss_hostname, port)
    else:
        server_socket = await make_normal_socket(client_socket, ss_hostname, port)
    try:
        if server_socket == None:
            return
        socket_data.create_data(client_socket, server_socket)
        socket_data.hostname[server_socket] = ss_hostname + ':' + str(port)
        with trio.CancelScope() as scope:
            async with trio.open_nursery() as nursery:
                try:
                    # Server_socket marked by 'ss' as the last parameter, writes to cs
                    nursery.start_soon(socket_received_chunk, client_socket, server_socket, 'ss')
                    # client_socket marked by 'cs' as the last parameter, writes to ss
                    nursery.start_soon(socket_received_chunk, client_socket, server_socket, 'cs')
                    # Write to client
                    nursery.start_soon(write_loop, client_socket, server_socket, socket_data.send_buffer[client_socket], 'cs')
                    # Write to server
                    nursery.start_soon(write_loop, client_socket, server_socket, socket_data.send_buffer[server_socket], 'ss')
                except trio.Cancelled:
                    pass

    except (EndSession, OSError, MemoryError, OverflowError, RuntimeError, WindowsError,
            BlockingIOError, BaseException, BaseExceptionGroup, trio.EndOfChannel, trio.BrokenResourceError) as e:
        print('Error Below:')
        print(e)
        print(e.args)
        # raise
    except KeyboardInterrupt:
        raise
    finally:
        print('-')
        print("connections were closed. nursery finished.")

async def make_normal_socket(client_socket, ss_hostname: str, port: int) -> trio.SocketStream | trio.SSLStream:
    """Setup normal socket
    """
    try:
        server_socket: trio.SocketStream | trio.SSLStream = \
            await trio.open_tcp_stream(ss_hostname, port, happy_eyeballs_delay=0.18)
    except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
            trio.BusyResourceError, gaierror, OSError,
            ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
            ConnectionError, BaseException):
        try:
            await socket_data.raw_send(client_socket, None,
                                       b"HTTP/1.0 502 Unable to connect to remote host.\r\n\r\n")
            await aclose_sockets(client_socket)
            return
        except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                trio.BusyResourceError, gaierror, OSError,
                ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                ConnectionError, BaseException):
            await aclose_sockets(client_socket)
            return
    return server_socket

async def make_SSL_socket(client_socket, ss_hostname: str, port: int):
    server_socket: trio.SSLStream | trio.SocketStream
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    try:
        server_socket: trio.SocketStream | trio.SSLStream = await trio.open_ssl_over_tcp_stream(
            ss_hostname,
            port,
            https_compatible=False,
            ssl_context=ssl_context,
            happy_eyeballs_delay=0.18)
    except (trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
            trio.BusyResourceError, gaierror, OSError,
            ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
            ConnectionError, BaseException):
        try:
            with trio.fail_after(17.8):
                await socket_data.raw_send(client_socket, None,
                                           b"HTTP/1.0 502 Unable to connect to remote host.\r\n\r\n")
                await aclose_sockets(client_socket)
        except (trio.TooSlowError, trio.ClosedResourceError, trio.TrioInternalError, trio.BrokenResourceError,
                trio.BusyResourceError, gaierror, OSError,
                ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError,
                ConnectionError, BaseException, BaseExceptionGroup):
            await aclose_sockets(client_socket)
            return None
    return server_socket

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
    line_count: int = 0
    while (client_socket in socket_data.mysockets) and (server_socket in socket_data.mysockets):
        if not line:
            try:
                popline = send_buffer.popleft().strip()
                line_count += 1
                if isinstance(popline, str):
                    line = popline.encode('utf8', errors="replace")
                else:
                    line = popline
            except IndexError:
                line = b''
                if line_count == 0:
                    await trio.sleep(0.100)
                line_count = 0
                await trio.sleep(0)
                continue
            line += b"\r\n"
        with trio.fail_after(28):
            try:
                if which_sock == 'cs':
                    if await script_command(client_socket, 'cs', line.strip()) is True:
                        continue
                    await client_socket.send_all(line)
                else:
                    if await script_command(client_socket, 'ss', line.strip()) is True:
                        continue
                    await server_socket.send_all(line)
                line = b''
                if line_count == 10:
                    line_count = 0
                    await trio.sleep(0.125)
                continue
            except (trio.BusyResourceError,trio.ClosedResourceError, OSError, gaierror, trio.TooSlowError,
                    ExceptionGroup, BaseException, BaseExceptionGroup, trio.BrokenResourceError,
                    ConnectionRefusedError, ConnectionResetError,
                    ConnectionAbortedError, ConnectionError, EndSession) as e:
                raise EndSession('WRITE LOOP Write Error. ' + which_sock + ' '+str(e)+' '+str(e.args))


async def script_command(client_socket, server, line):
    line = line.decode('utf8', errors="replace")
    line = line.split(' ')
    if line[0][0] == '@':
        line = line[1:]

    source = ''
    if line[0][0] == ':':
        source = line[0][1:]
        if len(line) >= 3:
            target = line[2]
        else:
            target = ''
        del line[0]
    if server == 'cs':
        source = socket_data.mynick[client_socket]
        if len(line) >= 2:
            target = line[1]
        else:
            target = ''
    low_line = ' '.join(line).lower()
    low_line = low_line.split(' ')
    if len(low_line) < 2:
        return False
    if low_line[1] == 'quit':
         if await UserCommands.user_QUIT(client_socket, server, source) is True:
            return True
    if low_line[1] == 'nick':
        if await UserCommands.user_NICK_change(client_socket, server, source, target) is True:
            return True
    if low_line[1] == 'part':
         if await UserCommands.user_PART(client_socket, server, source, target) is True:
            return True

    if source and len(low_line) >= 4 and len(low_line[3]) >= 3 and low_line[1] == 'privmsg' and low_line[3][1] == '.':
        source_nick = source.split('!')[0]
        target = target
        cmd = low_line[3][1:]
        if len(low_line) >= 5:
            parms = ' '.join(low_line[4:])
        else:
            parms = ''
        await UserCommands.execute_user_command(client_socket, server, source_nick, target, cmd, parms)
        return True
    else:
        source_nick = ''
        cmd = ''
        parms = ''
        target = ''

import translate

def isme(client_socket, server, nick, target='') -> bool:
    """Check if server is cs or nick is mynick or nick is
        *Status and return True or False
    Vars:
        :server: cs or ss
        :nick: nick to check
        :target: target nick to check
        :returns: bool
    """
    if server == 'cs':
        return True
    nick = nick.lower()
    if '!' in nick:
        nick = nick.split('!')[0]
    target = target.lower()
    if '!' in target:
        target = target.split('!')[0]
    if nick == socket_data.mynick[client_socket].lower() or target == '*status':
        return True
    else:
        return False
catch_all = {}
class UserCommands(object):
    @classmethod
    async def user_PART(cls, client_socket, server, source, chan) -> bool:
        source_full = source
        if '!' in source:
            source = source.split('!')[0]
        source = source.lower()
        return False

    @classmethod
    async def user_QUIT(cls, client_socket, source) -> bool:
        source_full = source
        if '!' in source:
            source = source.split('!')[0]
        source = source.lower()
        if '.script'+source in catch_all:
            del catch_all['.script'+source]
        return False

    @classmethod
    async def user_NICK_change(cls, client_socket, source, target) -> bool:
        source_full = source
        if '!' in source:
            source = source.split('!')[0]
        source = source.lower()
        if '.script' + source in catch_all:
            catch_all['.script'+target] = catch_all['.script' + source]
            del catch_all['.script' + source]
        return False

    @classmethod
    async def execute_user_command(cls, client_socket: trio.SocketStream | trio.SSLStream, server,
                                   source_nick, target_nick, cmd, parms) -> bool:
        """Execute a user command if it exists."""
        if '!' in source_nick:
            source = source_nick
            source_nick = source_nick.split('!')[0]
            target = target_nick
        target_nick = target_nick.lower()
        source_nick = source_nick.lower()
        if server == 'cs':
            source_nick = socket_data.mynick[client_socket].lower()
        try:
            await UserCommands.User_CMD[cmd](client_socket, server, source_nick, target_nick, cmd, parms)
        except (BaseException, BaseExceptionGroup) as e:
            # Write straight to a socket with a message for/to self (avoid the server when writting to self
            pass
async def ss_updateial(client_socket: trio.SocketStream | trio.SSLStream,
                       server_socket: trio.SocketStream | trio.SSLStream,
                       single_line: str, split_line: list[str]) -> \
        bool | None:
    """The function execution chain in reverse is
    updateial() -> ss_got_line() then fast_line()
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
    orig_upper_split: list[str] = colourstrip(single_line).split(' ')
    split_line: list[str] = colourstrip(single_line).lower().split()
    nick_src: str = single_line.split(' ')[0].split('!')[0].lower()
    src_nick_full: str = single_line.split(' ')[0].lower()
    upper_nick_src: str
    upper_nick_dest: str
    old_nick: str
    source_upper: str
    source: str
    my_usernick = socket_data.mynick[client_socket]
    if original_line[0] == '@':
        single_line = ' '.join(single_line.split(' ')[1:])
        orig_upper_split = original_line.split(' ')[1:]
        split_line = split_line[1:]
    if '!' in split_line[0] or '.' in split_line[0] and split_line[0][0] == ':':
        upper_nick_src: str = orig_upper_split[0].split('!')[0].lstrip(':')
        upper_nick_full_src: str = orig_upper_split[0]
        return_silent = ial.IALData.ial_add_nick(client_socket, nick_src, upper_nick_full_src.lower(), chan)
    if return_silent is True:
        return False
    return None


def cs_away_msg_notify(client_socket: trio.SocketStream | trio.SSLStream, nick: str, msg: str) -> None:
    """Notify the client that the user is away when joining the
      channel or talking in the channel
    Vars:
        :client_socket: the socket to the irc-client
        :nick: the string nickname that is set-away
        :msg: the string away-message, if any
        :return: None
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
    return lower_color_and_strip(text)


def lower_color_and_strip(text: str) -> str:
    """lower text, strip text, mirc colour removal
    :text: text to be stripped, lowered, and removed colour; to be parsed.
    :return: returns the string

    """
    text = text.lower()
    text = text.strip()
    text = colourstrip(text)
    return text


async def socket_received_chunk(client_socket: trio.SocketStream | trio.SSLStream,
                                server_socket: trio.SocketStream | trio.SSLStream, which_sock) -> None:
    """Read loop to receive data from the socket and pass it to
        cs/ss_received_line()

        :client_socket: client socket stream
        :server_socket: irc server socket stream
        :return: returns if the nursery needs to be closed.
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
    read_split: list[str] = []
    read_some: bytes
    read_some_found: int
    find_n: int = -1
    read_sock: bytes = b''
    read_count: int = 0
    while True:
        try:
            read_sock = await dest_socket.receive_some(2048)
        except trio.BusyResourceError:
            await trio.sleep(0.100)
            continue
        except trio.Cancelled:
            await trio.sleep(0)
            continue
        except (BaseException, BaseExceptionGroup, ExceptionGroup, trio.BrokenResourceError, trio.ClosedResourceError,
                trio.EndOfChannel, AttributeError) as e:
            print('IRC_server-Closed-Connection: ', e,e.args)
            # raise EndSession(e.args)
            return
        if not read_sock:
            raise EndSession(str(read_sock) + ' irc-server-closed-connection-to-proxy.')
        read_line += read_sock
        read_sock = b''
        while True:
            read_count = 0
            find_n = read_line.find(b'\n')
            if find_n == -1:
                break
            read_count += 1
            read_some_found = find_n + 1  # increase by one to read the find_n-1 character
            read_some = read_line[0:find_n + 1] # increase by one to account for 0 start
            read_str = usable_decode(read_some)
            read_str = read_str.strip()
            read_strip = lower_color_and_strip(read_str)
            read_split = read_strip.split(' ')
            read_strip = ''
            await rcvd_line(client_socket, server_socket, read_str, read_split)
            read_str = ''
            read_split = []
            read_some = b''
            remain = read_line[read_some_found:]
            read_line = remain
            if read_count == 10:
                read_count = 0
                await trio.sleep(0)
        if find_n == -1:
            read_str = ''
            read_strip = ''
            read_split = []
            read_sock = b''
            find_n = -1
            if read_line:
                await trio.sleep(0)
            else:
                await trio.sleep(0.160)
    return None


async def ss_received_line(client_socket: trio.SocketStream | trio.SSLStream,
                           server_socket: trio.SocketStream | trio.SSLStream, single_line: str,
                           split_line: list[str]) -> None:
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
        actions.sc_send(dest_socket, '\r\n')
        return
    if check_mirc_exploit(original_line) is True:
        await exploit_triggered(client_socket, server_socket)
        await trio.sleep(0)
        return None
    if (single_line.startswith('cap')):
        actions.sc_send(dest_socket, original_line)
        return
    if original_line[0] == '@':
        if not single_line.startswith('@time') and not single_line.startswith('@account') and not \
                single_line.startswith('@batch') and not single_line.startswith('@msgid'):
            print('Line starts with a new @ sign text')
            print('@@@@@@ @@@ @ @ ' + original_line)
            await trio.sleep(0)
        del split_line[0]
        single_line = ' '.join(split_line)
        orig_upper_split = original_line.split(' ')[1:]
    else:
        orig_upper_split = original_line.split(' ')

    ial_send = await ss_updateial(client_socket, server_socket, single_line,
                                  orig_upper_split)
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
            await trio.sleep(1)
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
            socket_data.state[client_socket]['connected'] = ctime()
    if split_line[0] == '376':
        # End of /motd
        if socket_data.state[client_socket]['motd_def']:
            socket_data.state[client_socket]['motd_def'] = 0
            await trio.sleep(0)
            return None
    elif split_line[0] == '005':
        sock_005(client_socket, original_line)
    elif split_line[0] in ("001", "372", "005", "376", "375", "422"):
        socket_data.state[client_socket]['doing'] = 'signed on'
        socket_data.mynick[client_socket] = split_line[2].lower()
        socket_data.state[client_socket]['upper_nick'] = orig_upper_split[2]
        socket_data.set_face_nicknet(client_socket)
    elif split_line[0] == '301':
        reason = " ".join(orig_upper_split[4:]).strip(':\r\n\t ')
        msg = f":{NAKED_URL} NOTICE {socket_data.mynick[client_socket]}" \
              f" :User {orig_upper_split[3]} is" \
              f" set away, reason: {reason}"
        actions.sc_send(client_socket, msg)


    xdcc_Line: str = split_line.join(' ')
    if fnmatch(xdcc_Line, "#?* *?x [???] ????*"):
        pass
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

    original_line = single_line
    single_line = single_line.lower()
    split_line_low: list[str] = single_line.split(' ')
    split_line: list[str] = original_line.split(' ')
    if split_line_low[0] == 'nick' and len(split_line) == 2:
        socket_data.mynick[client_socket] = split_line[1].lstrip(':')
    if split_line_low[0] == 'ping' or split_line_low[0] == 'pong':
        pass
    if split_line_low[0] == 'names':
        actions.sc_send(dest_socket, original_line)
        await trio.sleep(0)
        return

    len_split_line: int = len(split_line)
    if len_split_line == 1:
        actions.sc_send(dest_socket, original_line)
        await trio.sleep(0)
        return None
    halt_on_yes: bool | None = False
    # if split_line_low[1].startswith('.trio') or split_line_low[1].startswith('.proxy') or \
    #         split_line_low[1].startswith('.xdcc') or split_line_low[1].startswith('.py'):
    #     halt_on_yes = cs_rcvd_command(client_socket, server_socket, original_line, split_line_low)
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
    in_words = in_words.replace('week', 'wk')
    in_words = in_words.replace('day', 'dy')
    in_words = in_words.replace('hour', 'hr')
    in_words = in_words.replace('minute', 'min')
    in_words = in_words.replace('second', 'sec')
    return in_words


def send_motd(client_socket: trio.SocketStream | trio.SSLStream, mynick: str) -> None:
    """The replaced MOTD sent to the irc-client upon connecting. Add code to download
    motd from website, after connection and old motd has been sent. Notify user if there
    is a new motd, "/msg *status motd" for the latest.

    :client_socket: the socket to the irc-client
    :mynick: the string of irc-client nickname to send the MOTD to
    :returns: None

    """
    prefix = ':'+WWW_SHORT_URL +' 375 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + WWW_SHORT_URL + '  Message of the Day -')
    prefix = ':'+WWW_SHORT_URL +' 372 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + '\x02'+WWW_SHORT_URL+' MOTD\x02 -')
    actions.sc_send(client_socket, prefix)
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
    actions.sc_send(client_socket, prefix + "W-W-W: \x1fhttps://www.MyProxyIP.com/\x1f -")
    actions.sc_send(client_socket, prefix + "'X-Clacks-Overhead':\x02 'GNU Terry Pratchett' \x02-")
    prefix = ':'+WWW_SHORT_URL+' 376 ' + mynick + ' :- '
    actions.sc_send(client_socket, prefix + 'End of /MOTD -')
    return None


def cs_rcvd_command(client_socket: trio.SocketStream | trio.SSLStream,
                    server_socket: trio.SocketStream | trio.SSLStream,
                    single_line: str, split_line: list[str]) -> bool | None:
    """Received a command from the irc-client
    Vars:
        :client_socket: socket to irc-client
        :server_socket: socket to irc-server
        :single_line: single line string of text
        :split_line: single_line split on words
        :returns: bool of True to not relay to irc-server or None to relay to irc-server

    """

    del split_line[0]
    if len(split_line) >= 2 and split_line[2] == ':.colour':
        actions.sc_send(client_socket,
                        ':ashburry!mg-script@www.myircproxyip.com privmsg ashburry :colour is: ' + str(
                            ord(split_line[1][0]))
                        + ' = ' + split_line[1][0])
        # yes_halt = True to NOT send to server
        return True
    # Change to privmsg to *STATUS
    # if '.xdcc' in split_line[0].lstrip(':'):
    #     xdcc_system.xdcc_commands(client_socket, server_socket, single_line, split_line)
    #     return True
    # if '.trio' in split_line[0].lstrip(':') or '.proxy' in split_line[0]:
    #     proxy_commands.commands(client_socket, server_socket, single_line, split_line)
    #     return True
    # if 'url' in split_line[0].lstrip(':') and (len(split_line) >= 3):
    #     chan = single_line[1]
    #     url = ' '.join(split_line[2:])
    #     url, title, desc = get_url_desc(url)
    #     actions.sc_send(server_socket, f'privmsg {chan} :URL: {url}')
    #     actions.sc_send(server_socket, f'privmsg {chan} :Title: {title}')
    #     actions.sc_send(server_socket, f'privmsg {chan} :Description: {desc}')
    return None


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
    new_time: str = str(int(ctime()))
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


async def authenticate_proxy(auth_lines: list[str]) -> bool | str:
    """Check for bad login attempt parameters:
        Vars:
            :auth_lines: the remaining lines of text after the first line loops

    """
    i: int = 0
    len_lines: int = len(auth_lines)
    auth: str
    while True:
        if i > len_lines or len_lines == 0:
            del i
            del auth
            del len_lines
            del auth_lines
            return False
        auth = auth_lines[i].lower()
        if "proxy-authorization: basic" in auth:
            auth = auth_lines[i].split(" ")[2]
            break
        elif "authorization: basic" in auth:
            auth = auth_lines[i].split(" ")[2]
            break
        else:
            i += 1
    auth_user_pass: bool | list[str] = verify_login(auth)
    del i, auth, auth_lines, len_lines
    return auth_user_pass


def verify_login(auth_userlogin: str) -> bool | tuple[str, str]:
    """Validate user: pass login attempt
    Vars:
        :auth_userlogin: The `user: pass` login attempt
        :returns: bool True of ok False if not-ok

    """
    auth_pass: str = ''
    auth_user: str = ''
    try:
        auth_login: str = usable_decode(b64decode(auth_userlogin))
        auth_user = auth_login[:auth_login.find(":")]
        auth_user = auth_user.strip()
        auth_user = auth_user.lower()
        auth_pass = auth_login[auth_login.find(":") + 1:].strip()
        if not auth_pass or not auth_user or len(auth_user) > 50 or len(auth_pass) > 40:
            return False
        if auth_login.count(":") > 1 or auth_login.count(':') < 1 or auth_login.count(" ") > 0 \
                or verify_user_pwdfile(auth_user, auth_pass) is False:
            return False
        return (auth_user, auth_pass)
    except ValueError:
        return False
    finally:
        auth_pass = "a" * len(auth_pass)
        auth_user = "a" * len(auth_user)
        auth_login = 'a' * len(auth_login)
        auth_userlogin = 'a' * len(auth_userlogin)
        del auth_login
        del auth_userlogin
        del auth_pass
        del auth_user




async def proxy_server_handler(cs_before_connect: trio.SocketStream) -> None:
    """Handle a connection to the proxy server.
                        Accept proxy http/1.0 protocol.
        vars:
        :@param cs_before_connect: the socket already accepted and
                        ready for reading (1 byte at a time).
        :@return: None
    """
    global identd_list
    # Write down tries per minute for this IP. And just close them all if its too many.
    try:
        hostname: str = cs_before_connect.socket.getpeername()[0].lower()
        identd_list.append([hostname,ctime()])
    except (BaseException, BaseExceptionGroup):
        await cs_before_connect.aclose()
        print('socket closed due to invalid hostname')
        return
    if not (check_fry_server):
        await aclose_sockets(cs_before_connect)
        print(':::::: FRY_SERVER TRIGGERED ::::::')
        return None
    socket_data.hostname[cs_before_connect] = hostname
    port = f'{cs_before_connect.socket.getsockname()[1]}'
    socket_data.echo(cs_before_connect, "Accepted a client connection " + hostname + " on port " + str(port) + '...')
    byte_string_data: bytes = b''
    auth: bool | None | tuple[str, str] | list[str, str]
    bytes_data: bytes
    byte_string: str = ''
    with trio.move_on_after(60) as cancel_scope:
        while True:
            bytes_data: bytes = await cs_before_connect.receive_some(1)
            byte_string_data += bytes_data
            if not byte_string_data.endswith(b"\r\n\r\n"):
                continue
            break
    if cancel_scope.cancelled_caught:
        await aclose_sockets(cs_before_connect)
        socket_data.echo(cs_before_connect, "Client is too slow to send data. Socket closed.")
        await trio.sleep(0)
        raise EndSession('Client closed connection. Make sure your client is set to use Proxy not SOCKS.')
    try:
        auth = False
        while b'\r' in byte_string_data:
            byte_string_data = byte_string_data.replace(b"\r", b"\n")
        while b"\n\n" in byte_string_data:
            byte_string_data = byte_string_data.replace(b"\n\n", b"\n")
        while b"  " in byte_string_data:
            byte_string_data = byte_string_data.replace(b"  ", b" ")
        lines: list[bytes] = byte_string_data.split(b"\n")
        str_lines: list[str] = []
        for line in lines:
            str_lines.append(usable_decode(line.strip()))
        del line
        i = 0
        while True:
            if i >= len(str_lines):
                break
            if (str_lines[i]) == '':
                del str_lines[i]
                continue
            i += 1
        if len(str_lines) > 1:
            auth = await authenticate_proxy(str_lines)
        if not auth:
            await aclose_sockets(cs_before_connect)
            return None
        socket_data.login[cs_before_connect] = auth[0]
        if cs_before_connect not in socket_data.state:
            socket_data.state[cs_before_connect] = {}
            socket_data.state[cs_before_connect]['doing'] = "connecting"
            if 'by_username' not in system_data.user_settings:
                system_data.user_settings['by_username'] = {}
            if auth[0].lower() not in system_data.user_settings['by_username']:
                system_data.user_settings['by_username'][auth[0].lower()] = set()
            system_data.user_settings['by_username'][auth[0].lower()].add(cs_before_connect)
        try:
            await before_connect_sent_connect(cs_before_connect, str_lines[0])
        except EndSession:
            pass
    finally:
        await aclose_both(cs_before_connect)


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
        await aclose_sockets(cs_sent_connect)
        return None
    if words[0] != "connect":
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 Bad Request. Proxy use only for IRC networks.\r\n\r\n".encode()
        )
        await aclose_sockets(cs_sent_connect)
        return None
    host: str = words[1]

    if ":" not in host:
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 Bad Request. Requires `server:port` to connect to.\r\n\r\n".encode()
        )
        await aclose_sockets(cs_sent_connect)
        return None
    server: str = ':'.join(host.split(":")[0:-1])
    port: str = host.split(":")[-1]
    try:
        port_num: int = int(port)
    except ValueError:
        await cs_sent_connect.send_all(
            "HTTP/1.0 400 bad request. requires integer port number.\r\n\r\n".encode()
        )
        await aclose_sockets(cs_sent_connect)
        return None
    print('checkpoint: proxy_make_irc_connect')
    await proxy_make_irc_connection(cs_sent_connect, server, port_num)


async def start_proxy_listener():
    """Start the proxy server.

    """
    if Settings_ini.has_section('settings') is False:
        Settings_ini.add_section('settings')

    listen_ports: str = system_data.Settings_ini["settings"].get("listen_ports", '4321')
    listen_ports = listen_ports.replace(',', ' ').replace(';', ' ').replace('  ', ' ') \
        .replace('*', '').replace('+', '').replace('\t', ' ').strip()
    while '  ' in listen_ports:
        listen_ports = listen_ports.replace('  ', ' ')

    listen_ports_list: list[str] = listen_ports.split(' ')
    try:
        print('-')
        print("Started Proxy-Server. Default login is 'user : pass'")
        async with trio.open_nursery() as nursery:
            for f in listen_ports_list:
                if not f.isdigit():
                    continue
                nursery.start_soon(trio.serve_tcp, proxy_server_handler, int(f))
                print("proxy is ready, listening on port " + str(f))
            # nursery.start_soon(trio.serve_tcp, identd_handler, 113)
            print('Started Identd server')
            print("press Ctrl+C to quit...\n")
    except (EndSession, BaseException, BaseExceptionGroup,
            KeyboardInterrupt, OSError, gaierror) as exc:
        if len(exc.args) > 1 and (exc.args[0] == 98 or exc.args[0] == 10048):
            print(
                '\nERROR: the listening port is being used somewhere else. '
                + 'maybe trio-ircproxy.py is already running somewhere?')

            await quit_all()
            # raise
            # print("EXC: " + str(exc.args))
        else:
            # raise
            pass
    print("\nTrio-ircproxy.py has Quit! -- good-bye bear ʕ•ᴥ•ʔ\n")
    try:
        sys.exit(13)
    except SystemExit:
        os._exit(130)


async def quit_all() -> None:
    """send a quit message and close all sockets.

    """
    sockets = socket_data.mysockets
    for sock in sockets:
        if socket_data.which_socket[sock] != 'cs':
            continue
        try:
            await actions.send_quit(sock)
        except:
            continue
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
