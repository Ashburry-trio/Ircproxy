from __future__ import annotations

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
from ssl import create_default_context
from ssl import Purpose
from sys import argv
from threading import Timer
from time import time
from typing import Deque
from chardet import detect
import sys
import os
from cryptography.fernet import Fernet



async def authenticate_proxy(client_socket: trio.SocketStream, auth_lines: list[str]) -> bool | tuple[str, str]:
    """Check for bad login attverify_userempt
        parameters:

        :client_socket: client socket
        :auth_lines: the remaining lines of text after the first line

    """
    i = 0
    while True:
        if i > len(auth_lines):
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
            await client_socket.send_all(b"407 You need an login to continue.\r\n")
            await client_socket.send_all(
                b'WWW-Authenticate: Basic realm="trio-ircproxy user'
                + b' realm", charset="UTF-8"\r\n\r\n'
            )
        await client_socket.aclose()
        return False
    if auth_words_split[0].lower() != "basic":
        socket_data.echo(client_socket, "Disconnected, invalid authentication type attempt.")
        with trio.move_on_after(5):
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
        with trio.move_on_after(5) as cancel_scope:
            await client_socket.send_all(b"401 Unauthorized. Bad username/password"
                                         + b" attempt.\r\n\r\n")
        raise EndSession('bad username/password', client_socket)
    return name


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
    while (client_socket in socket_data.mysockets) and (server_socket in socket_data.mysockets):
        try:
            line = str(usable_decode(send_buffer.popleft()).rstrip())
            #line = line[1:-1]
            print('which_sock: '+line)
        except IndexError:
            await trio.sleep(0.3)
            continue
        line += "\n"
        if not isinstance(line, bytes):
            line = line.encode("utf-8", errors="replace")
        with trio.fail_after(60):
            try:
                if which_sock == 'ss':
                    await server_socket.send_all(line)
                else:
                    await client_socket.send_all(line)
            except (trio.BrokenResourceError, trio.ClosedResourceError, gaierror,
                    trio.TooSlowError, trio.BusyResourceError, OSError, BaseException) as exc:
                print('write error! ' + which_sock + ' ' + str(exec) + ' '
                      + str(exc.args) + ' LINE: ' + str(line))
                raise EndSession('Write Error. ' + which_sock + ' ' + str(line))
            await trio.sleep(0)
            continue

def verify_login(auth_userlogin: str) -> bool | tuple[str, str] | bool:
    """Validate user: pass login attempt

        :@param auth_userlogin: The `user: pass` login attempt
        :@return: bool True of ok False if not-ok

    """
    auth_pass: str = ''
    auth_user: str = ''
    try:
        auth_login: str = usable_decode(b64decode(auth_userlogin))
        print(auth_login)
        auth_pass: str = auth_login[auth_login.find(":") + 1:]
        auth_user: str = auth_login[:auth_login.find(":")]
        auth_user: str = auth_user.strip()
        auth_user: str = auth_user.lower()
        if not auth_pass or not auth_user or len(auth_user) > 40 or len(auth_pass) > 40:
            return False
        if auth_login.count(":") > 1 or auth_login.count(':') < 1 or auth_login.count(" ") > 1 \
                or verify_user_pwdfile(auth_user, auth_pass) is False:
            return False
        return (auth_user, auth_pass)
    except ValueError:
        return False
    finally:
        auth_pass = "a" * len(auth_pass)
        auth_user = "a" * len(auth_user)
        del auth_pass
        del auth_user



async def proxy_make_irc_connection(cs_waiting_connect: trio.SocketStream
                                                        | trio.SSLStream, ss_hostname: str, port: int) -> None:
    """Make a connection to the IRC network and fail (502) if unable to connect.
    vars:
        :type server: str
        :@param cs_awiting_connect: the client socket
        :@param server: a string of the server to connect to
        :@param port: the port number to connect to (integer)
        :@return: returns None


    """
    # print("making irc connection")
    ss_hostname = ss_hostname.lower()
    server_socket: trio.SocketStream | trio.SSLStream
    client_socket: trio.SocketStream | trio.SSLStream
    server_socket_nossl: trio.SocketStream | trio.SSLStream
    client_socket_nossl: trio.SocketStream | trio.SSLStream
    try:
        client_socket_nossl = cs_waiting_connect
        server_socket_nossl = await trio.open_tcp_stream(ss_hostname, port, happy_eyeballs_delay=1.15)
    except (gaierror, ConnectionRefusedError, OSError, ConnectionAbortedError, ConnectionError):
        await socket_data.raw_send(cs_waiting_connect, None,
                                   b"HTTP/1.0 502 Unable to connect to remote host.\r\n\r\n")
        await aclose_sockets(sockets=(cs_waiting_connect,))
        return None
    try:
        granted: bytes = b"HTTP/1.0 200 connection started with irc server.\r\n\r\n"
        if not await socket_data.raw_send(client_socket, server_socket, granted):
            return None
        if port in (6697, 9999, 443, 6699, 6999, 7070) and \
                ss_hostname != 'irc.undernet.org' and (port == 7000 and ss_hostname != 'irc.dal.net'):
            context_ssl = create_default_context()
            server_socket_ssl = trio.SSLStream(server_socket_nossl, context_ssl,
                                               server_hostname=ss_hostname, https_compatible=False)
            server_socket = server_socket_ssl
            client_socket = server_socket_nossl
            del server_socket_ssl
        else:
            server_socket = server_socket_nossl
            client_socket = client_socket_nossl
        del server_socket_nossl
        del client_socket_nossl

        socket_data.create_data(client_socket, server_socket)
        socket_data.hostname[server_socket] = ss_hostname + ':' + str(port)

        async with trio.open_nursery() as nursery:
            nursery.start_soon(ss_received_chunk, client_socket, server_socket)
            nursery.start_soon(cs_received_chunk, client_socket, server_socket)
            # Write to client
            nursery.start_soon(write_loop, client_socket, server_socket,
                               socket_data.send_buffer[client_socket], 'cs')
            # Write to server
            nursery.start_soon(write_loop, client_socket, server_socket,
                               socket_data.send_buffer[server_socket], 'ss')
            # maybe add a command loop for non async scripts to follow snf execute.
    except (BaseException, EndSession, BaseExceptionGroup):
        socket_data.clear_data(client_socket)
        await aclose_both(client_socket)
        # return
        raise
    finally:
        # proxy_make_irc_connection()
        print("connections were closed. nursery finished!")


async def ss_received_chunk(client_socket: trio.SocketStream | trio.SSLStream,
                            server_socket: trio.SocketStream | trio.SSLStream) -> bool | None:
    """Read loop to receive data from the socket and pass it to
        fast_line_split_for_read_loop()

        :@param client_socket: client socket stream
        :@param server_socket: irc server socket stream
        :@return: returns if the nursery needs to be closed.
    """
    while True:
        rcvd_bytes = await server_socket.receive_some(100000)
        await client_socket.send_all(rcvd_bytes)
        print(rcvd_bytes)
        await trio.sleep(0)

async def cs_received_chunk(client_socket: trio.SocketStream | trio.SSLStream,
                            server_socket: trio.SocketStream | trio.SSLStream) -> None:
    """
    Receive a chunk of data and call cs_received_line() when atleast one line has completed
    @param client_socket: the socket to the irc-client
    @param server_socket: the socket to the irc-server
    @return: None.

    """
    bytes_cap: int = 0
    byte_string: str = ''
    max_RECV: int = 355350000
    bytes_data: bytes = b''
    await trio.sleep(0)
    while True:
        bytes_data = await client_socket.receive_some(100000)
        await server_socket.send_all(bytes_data)
        print(bytes_data)
        await trio.sleep(0)

def get_words(text: str) -> list:
    """Returns the words list of the first line in list

        vars:
            :@param text: A string of text with lines ending in cr, lf, and crlf
            :@return: a list of words split on whitespace.

    """
    try:
        text = text.rstrip()
        lower_string: str = text.lower()
        lower_string = lower_string.replace("\r", "\n")
        lower_string = lower_string.replace("\f", "\n")
        while "\n\n" in lower_string:
            lower_string = lower_string.replace("\n\n", "\n")
        return lower_string.split(' ')
    except ValueError:
        return ['', ]


def usable_decode(text: bytes) -> str:
    """Decode the text so it can be used.
        vars:
            :@param text: a string of bytes that needs decoding
            :@return: string of decoded bytes (text)

    """
    try:
        decoded_text: str
        decoded_text = text.decode("utf8")
    except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
        try:
            decoded_text = text.decode("latin1")
        except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
            try:
                det = detect(text)
                decoded_text = text.decode(det['encoding'], errors="replace")
            except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
                return ''
    return decoded_text


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


class EndSession(BaseException):
    """
    An BaseException to raise when paired sockets are closed.
    """

    def __init__(self, args: str | None = '', close_socket: trio.SocketStream | trio.SSLStream | None = None):
        self.args: list[str] = [str(args)]
        if close_socket is not None:
            socket_data.clear_data(close_socket)



async def proxy_server_handler(cs_before_connect: trio.SocketStream) -> None:
    """Handle a connection to the proxy server.
                        Accept proxy http/1.0 protocol.
        vars:
        :@param cs_before_connect: the live socket already accepted and
                        ready for reading (1 byte at a time).
        :@return: None
    """
    # Write down tries per minute for this IP. And just close them all if its too many.
    hostname: str = cs_before_connect.socket.getpeername()[0]
    print(hostname)

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
        except (BaseException, EndSession, trio.Cancelled,trio.BrokenResourceError,
                trio.ClosedResourceError, trio.BusyResourceError, trio.TrioInternalError) as exc:
            print("handler EXCEPT 1: " + str(exc.args))
            await aclose_both(cs_before_connect)
            socket_data.clear_data(cs_before_connect)
            return
    try:
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
        # username and password login
        if cs_before_connect not in socket_data.state:
            socket_data.state[cs_before_connect] = {}
            socket_data.state[cs_before_connect]['doing'] = "connecting"
            if 'by_username' not in system_data.user_settings:
                system_data.user_settings['by_username'] = {}
            if auth[0] not in system_data.user_settings['by_username']:
                system_data.user_settings['by_username'][auth[0]] = set()
            system_data.user_settings['by_username'][auth[0]].add(cs_before_connect)
        async with trio.open_nursery() as nursery:
            nursery.start_soon(before_connect_sent_connect, cs_before_connect, lines[0])
    except (BaseException, EndSession) as exc:
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
    except (EndSession, BaseException, BaseExceptionGroup, Exception, \
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




trio.run(start_proxy_listener)