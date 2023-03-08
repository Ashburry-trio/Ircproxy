Trio-ircproxy.py - an proxy server for your IRC client. Copyright (c) 2023,
Master Sire G.I. Kenggi Peters phd. ret.

This is a work in progress, if you wish to help then submit a pull request
and/or write issues for all and any requests. The issues is working as an to-do
list of features.

Issues (requests) List :
`https://github.com/ashburry-chat-irc/trio-ircproxy/issues` \# Setup

- Download and Install `Python 3.11` or later from `https://www.python.org/downloads/`

- Download clink setup.exe from `https://github.com/chrisant996/clink/releases`

- Extract trio-ircproxy.zip to %UserProfile% - open `file explorer` by right
clicking on the `Windows Start Menu` button and choose `file explorer`

- navigate `file explorer` to `%UserProfile%\trio-ircproxy` directory

- double click on `install.bat` just once after extraction `of trio-ircproxy.zip` 

- run apps with a double click on `runall.bat` 

- load `mIRC-Load_This_in_Remotes-INSTALL.mrc` in mirc/adiirc remotes section

Keep in mind that your `trio-ircproxy` folder may have the name
`trio-ircproxy-main`. Also the usage of `%UserProfile%` is a windows shortcut to
your home directory which is `c:\users\USER\` replace `USER` with your actual
`username`. If you do not know your username then try using `%UserProfile%`
which will expand to your user home directory such as `c:\user\USER\` It is
the same as ~ on linux.

To deploy
on `PythonAnywhere.com`:

-   Create an zip file of two directories, first is `trio-ircproxy\scripts\www`
    and second is `trio-ircproxy\scripts\website_and_proxy`

-   Upload zip file to PythonAnywhere.com in the `/home/username/` directory.
    Replace `username` with your `pythonanywhere.com username`.

-   Open a terminal on `PythonAnywhere`

-   In terminal type `unzip file.zip -d .` (notice the unzip command ends with
    an period)

-   Edit the `www\www-server-config.ini` so the `web-server-hostname` is that of
    `your webserver` put `username.pythonanyhwere.com` without the http(s).
     And the port is set to `80 or 443` use 443 for `encryption`.

-   On the `PythonAnywhere.com` website: edit your `www/www-server-config.ini`
    put your URL (username.pythonanywhere.com) for `web-server-hostname` and set
    the `web-server-port` to `80 or 443` it is not used.

-   `Reload your web-server` from the `WEB tab` on `PythonAnyhwere.com`.

Copyright License
=================

BSD 3-Clause License Copyright (c) 2023, Master Sire GI Kenggi J.P. phd. ret.
All rights reserved. Please read CODE_OF_CONDUCT.md and if you may, see file
`LICENCE` for a short read.
