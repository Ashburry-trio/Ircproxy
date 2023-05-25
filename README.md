**Trio-ircproxy.py** - an proxy/bounce server for your IRC client. Copyright (c)
2023, *Master Sire G.I. Kenggi J.P. phd. ret.*

This is a work in progress, if you wish to help then write issues for all and
any requests. The issues is working as an to-do list of features as well as a
communication channel.

Issues (requests) List :
**https://github.com/ashburry-chat-irc/trio-ircproxy/issues**

-   Download and Install **Python 3.11** or later from
    **https://www.python.org/downloads/** it should work on Python 3.8 but I
    have not tested it, yet.

-   Download clink setup.exe from
    **https://github.com/chrisant996/clink/releases** and install

-   open **cmd.exe** by *right clicking* on the **Windows Start Menu** button
    and choose **run**

-   type in the input box **cmd.exe** and press **Enter**

-   Extract **trio-ircproxy-main.zip** by typing at the prompt **cd
    %UserProfile%**\Downloads***\* and then** unzip trio-ircproxy-main.zip -d
    %UserProfile%\Documents\\\*\* or use your favorite zip application such as
    7-zip.

-   at the command prompt type \*\*cd %UserProfile%\Documents*\*

-   type *dir/w* to list the files then **cd trio-ircproxy** or **cd
    trio-ircproxy-main**

-   type **install.bat -3.11** the *-3.11* is the *Python version* you have
    installed.

-   load **mIRC-Load_This_in_Remotes-INSTALL.mrc** in mirc/adiirc *remote
    section* and choose **YES** to *initialize script*.

Keep in mind that your **trio-ircproxy** folder may have the name
**trio-ircproxy-main**. Also the usage of **%UserProfile%** is a windows
shortcut to your home directory which is *c:*\users\USER*\* replace* USER\* with
your actual *username*. If you do not know your username then try using
**%UserProfile%** and if you have linux running you can also use **\~Documents**
which will expand to your *user home folder* such as *c:\\user\\USER\\*. If you
have **OneDrive** installed then I suggest using your **Home folder** (your
**%UserProfile% folder**) to hold your *trio-ircproxy* application or
*uninstall* OneDrive and delete its folder if necessary.

Copyright License
=================

BSD Zero-Clause License Copyright (c) 2023, Master Sire GI Kenggi J.P. phd. ret.
All rights reserved. Please read *CODE_OF_CONDUCT.md* if you may, and see file
*LICENCE* for a short read if you plan on using Trio-Ircproxy.py to make money
or changes.

There are no instructions to run the *web-server* half; this is because I will
be running one website for all *trio-ircproxy installations*. This will make
things much easier and *free* for everyone. The website can be accessed at
**https://www.mslscript.com**

Soon, you won’t have to install Trio-Ircproxy.py because it will be hosted on a
cloud-compute server with several IPs to choose from this will allow masking of
your IP address making ZNC obsolete (right now it is compatible with ZNC.) The
/server line of ZNC is complicated and hard to remember and does not auto-save
on the command line. A Proxy server is much better but your client must support
Proxy servers (which is all of them at this time).
