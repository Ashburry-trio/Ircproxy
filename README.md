**Trio-ircproxy.py** - an proxy/bounce server for your IRC client. Copyright (c) 2023,
*Master Sire G.I. Kenggi J.P. phd. ret.*

This is a work in progress, if you wish to help then write issues for all and any requests. The issues is working as an to-do list of features.

Issues (requests) List :
**https://github.com/ashburry-chat-irc/trio-ircproxy/issues** 

-   Download and Install **Python 3.11** or later from
    **https://www.python.org/downloads/**

-   Download clink setup.exe from
    **https://github.com/chrisant996/clink/releases** and install

-   Extract **trio-ircproxy.zip** to **%UserProfile%\Documents\**

-   open **cmd.exe** by right clicking on the **Windows Start Menu** button and choose **run**

-   choose to run **cmd.exe**

-   at the command prompt type **cd %UserProfile%\Documents**

-   type *dir/w* to list the files then **cd trio-ircproxy** or **cd
    trio-ircproxy-main**

-   type **install.bat -3.11** the *-3.11* is the *Python version* you have installed.

-   load **mIRC-Load_This_in_Remotes-INSTALL.mrc** in mirc/adiirc remotes section

Keep in mind that your **trio-ircproxy** folder may have the name
**trio-ircproxy-main**. Also the usage of **%UserProfile%** is a windows shortcut to
your home directory which is *c:\users\USER\* replace *USER* with your actual
*username*. If you do not know your username then try using **%UserProfile%**
which will expand to your *user home directory* such as *c:\\user\\USER\\* it is
the same as \~ on linux.

To deploy on *PythonAnywhere.com*:

-   Upload **\\trio-ircproxy\\scripts\\deploy.zip** file to *PythonAnywhere.com*
    in the **/home/username/** directory. Replace *username* with your
    pythonanywhere.com username.

-   Open a bash terminal on `PythonAnywhere`

-   In terminal type **unzip deploy.zip -d .** (notice the unzip command ends
    with an period). Unzip in the *root home directory*.

-   On your computer edit the
    **\\trio-ircproxy\\scripts\\www\\www-server-config.in**`i` so the
    **web-server-hostname** is that of your webserver put
    *username.pythonanyhwere.com* without the http(s). And the port is set to*
    80 or 443 *use 443 for encryption\`.

-   On the **PythonAnywhere.com** website: edit your
    **/www/www-server-config.ini** put your URL

(*username.pythonanywhere.com*) for **web-server-hostname** and set the
**web-server-port** to** ***80 or 443*.

-   Go to your `WEB tab` by clicking the hamburger on the top left corner.

-   In the **WEB tab** set the **source code** to `/home/username/www/` with
    username as your PythonAnywhere.com username.

-   Edit the **WSGI configuration file** to look like this below:

 

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
# add your project directory to the sys.path
project_home = '/home/USERNAME/www/'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from flask_app import app as application

On the "project_home" line change USERNAME to your PythonAnywhere username. Uncomment "import sys"

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-   Click **SAVE** then click the hamburger to go to the** WEB tab** and
    click-on **reload website.com** at the top.

Copyright License
=================

BSD 3-Clause License Copyright (c) 2023, Master Sire GI Kenggi J.P. phd. ret.
All rights reserved. Please read CODE_OF_CONDUCT.md and if you may, see file
`LICENCE` for a short read.
