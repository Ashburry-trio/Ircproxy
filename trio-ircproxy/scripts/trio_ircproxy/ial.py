#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

from fnmatch import fnmatch
from typing import Union, List, Dict, Set
from threading import Timer
import trio
from socket_data import SocketData as socket_data

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

class IALData:
    myial: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = dict()
    myial_chan: Dict[trio.SocketStream | trio.SSLStream, Dict[str, Set[str]]] = dict()
    myial_count: Dict[trio.SocketStream | trio.SSLStream, Dict[str, int]] = dict()
    timers: Set[Timer] = set()
    who: Dict[trio.SocketStream | trio.SSLStream, Dict[str, str]] = dict()

    @classmethod
    def sendwho(cls, server_socket: trio.SocketStream | trio.SSLStream, th: Timer, chan: str):
        print('WHO SENT: ',chan)
        sc_send(server_socket, 'who ' + chan)
        cls.timers.remove(th)

    @classmethod
    def comchans_get_set(cls, client_socket: trio.SocketStream | trio.SSLStream, nick: str) -> frozenset:
        """Return the common channels with nick.
        Vars:
            :client_socket: trio.SocketStream | trio.SSLStream() irc client socket stream
            :nick: nick or nickmask to common channels with
            :return: returns a set of strings of common channel names
        """
        cls.make_ial(client_socket)
        if not nick:
            nick = ''
        elif "!" in nick:
            nick = nick.split("!")[0]
        if nick in cls.myial_chan[client_socket]:
            return frozenset(cls.myial_chan[client_socket][nick])
        else:
            return frozenset([])

    @classmethod
    def comchans_get_list(cls, client_socket: trio.SocketStream | trio.SSLStream, nick: str) -> List[str]:
        """Return the common channels with nick.
        Vars
            :client_socket: trio.SocketStream | trio.SSLStream() irc client socket stream
            :nick: nick to common channels with
            :return: returns a list of strings of common channel names

        """
        cls.make_ial(client_socket)
        return list(cls.comchans_get_set(client_socket, nick))

    @classmethod
    def ial_get_masks(cls, client_socket: trio.SocketStream | trio.SSLStream, mask: str) -> frozenset:
        """Retrieve an nickmask from the global IAL

        Vars:
            :client_socket: the client socket
            :mask: '*!*@*addr.net'
            :return: a frozenset() of matches
        """
        found_ial = set()
        for nick in cls.myial[client_socket]:
            fullnick = cls.myial[client_socket][nick]
            if fnmatch(fullnick, mask):
                found_ial.add((nick, fullnick))
        return frozenset(found_ial)

    @classmethod
    def ial_get_fullnick(cls, client_socket: trio.SocketStream | trio.SSLStream, nick: str) -> str:
        """Returns full address of nickname.
            Vars:
                :param client_socket: client socket
                :param nick: just a nickname
                :returns: the full complete nickmask of the nickname
        """
        cls.make_ial(client_socket)
        if nick in cls.myial[client_socket]:
            return cls.myial[client_socket][nick]
        else:
            return ''

    @classmethod
    def ial_count_nicks(cls, client_socket: trio.SocketStream | trio.SSLStream, chan: str):
        count: int = 0
        for nick in cls.myial_chan[client_socket]:
            if chan in cls.myial_chan[client_socket][nick]:
                count += 1
        return count

    @classmethod
    def ial_add_newnick(cls, client_socket: trio.SocketStream | trio.SSLStream, oldnick: str, newnick: str, nickmask: str) -> None:
        """Replaces oldnick with newnick
        vars:
            :client_socket: client socket
            :oldnick: the old nickname
            :newnick: the new nickname
            :nickmask: the new nickmask that may change
        """
        cls.make_ial(client_socket)
        cls.myial[client_socket][newnick] = nickmask
        if oldnick == newnick:
            return
        if newnick not in cls.myial_chan[client_socket]:
            cls.myial_chan[client_socket][newnick] = set()
        if oldnick in cls.myial_chan[client_socket]:
            chans = cls.myial_chan[client_socket][oldnick]
            cls.myial_chan[client_socket][newnick].update(chans)
        cls.ial_remove_nick(client_socket, oldnick, None)

    @classmethod
    def ial_remove_nick(cls, client_socket, old_nick, chans: list[set, str | None]) -> None:
        """Removes nick from ial
        Vars:
            :old_nick: nick to remove
            :client_socket: client socket
            :chans: set, str or None
        """
        cls.make_ial(client_socket)
        try:
            returns = False
            if chans is not None:
                if isinstance(chans, set) or isinstance(chans, list) or isinstance(chans, tuple):
                    for chan in chans:
                        if chan in cls.myial_chan[client_socket][old_nick]:
                            returns = True
                        cls.myial_chan[client_socket][old_nick].discard(chan)

                elif chans:
                    if chans in cls.myial_chan[client_socket][old_nick]:
                        returns = True
                    cls.myial_chan[client_socket][old_nick].discard(chans)
            if not chans or not cls.myial_chan[client_socket][old_nick]:
                try:
                    del cls.myial_chan[client_socket][old_nick]
                    returns = True
                except KeyError:
                    pass
                try:
                    del cls.myial[client_socket][old_nick]
                    returns = True
                except KeyError:
                    pass
        except KeyError:
            pass
        return returns
    @classmethod
    def ial_remove_chan(cls, client_socket, chan) -> None:
        """Remove a chan from the ial.

        vars:
            :client_socket: client socket
            :chan: chan to remove
        """
        cls.make_ial(client_socket)
        print(f'timers: {cls.timers}')
        try:
            removed = []
            for nick in cls.myial_chan[client_socket]:
                cls.myial_chan[client_socket][nick].discard(chan)
                if not cls.myial_chan[client_socket][nick]:
                    removed += [nick]
            for nick in removed:
                del cls.myial_chan[client_socket][nick]
                del cls.myial[client_socket][nick]
            del cls.myial_count[client_socket][chan]
            # Remove the Timer
        except KeyError:
            # This should not happen
            pass

    @classmethod
    def ial_add_nick(cls, client_socket, nick, nickmask, chan) -> bool:
        """Add a nickname to the ial. for now chan maybe None, this will change sometime.
        vars:
            :client_socket: client socket
            :nick: nickname to add
            :nickmask: the full address of the nickname
            :chan: add an common channel to the ial
            :returns: None
        """
        cls.make_ial(client_socket)
        cls.myial[client_socket][nick] = nickmask

        if nick not in cls.myial_chan[client_socket]:
            cls.myial_chan[client_socket][nick] = set()
        if chan:
            cls.myial_chan[client_socket][nick].add(chan)
        return False

    @classmethod
    def make_ial(cls, client_socket) -> None:
        """Make the client_socket ial dict
            Vars:
                :client_socket: the client socket
                :returns: None
        """
        if client_socket not in cls.myial:
            cls.myial[client_socket] = {}
        if client_socket not in cls.myial_chan:
            cls.myial_chan[client_socket] = {}
        if client_socket not in cls.who:
            cls.who[client_socket] = dict()


















