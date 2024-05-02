**Trio-ircproxy.py** 
=====================

### \- an proxy/bounce server for your IRC client. Copyright (c) 2024, *Master Sire G.I. Kenggi J.P. phd. ret.*

This is a work in progress, if you wish to help then write issues for all and
any requests. The issues is working as a to-do list of features as well as a
communication channel.

Issues (requests) List :
**https://github.com/ashburry-trio/Ircproxy/issues**

This application is not meant to be run by a user, instead I will rent a VPS to
host the application with on a few dozen IP addresses and it will be networked
with *https://www.myproxyip.com/*.

If you wish to run the application, maybe just to see if it is still working
then follow the instructions below. If you are using Linux it is assumed you
know how to run the app from these Windows only instructions:

-   open **cmd.exe** by *right clicking* on the **Windows Start Menu** button
    and choose **run**

-   type in the input box **cmd.exe** and press **Enter**

-   Extract **ircproxy.zip** by typing at the prompt **cd
    %UserProfile%\\Downloads** and then **unzip ircproxy.zip -d
    %UserProfile%** or use your favorite zip application such as
    7-zip.

-   at the command prompt type **cd %UserProfile%\\Ircproxy**

-   type **install.bat -3.12** the *-3.12* is the *Python version* you have
    installed. Install the latest version and use **py --version** to see your
    installed python versions.

-   If you are using Linux do not update your systems version of Python, instead
    create a virtual-environment with the latest version in the folder specified
    below.

If you are using Linux then you need to install manually; this is done with:

**python3.12 -m venv ~/Ircproxy/trio-ircproxy/venv** then look in **./trio-ircproxy/venv/bin** 
for the **activate** script compatible with your Linux version. Then use
google to see how to run it. You will need to *activate* the the venv everytime
you run the app. After you have activated the venv type **python3.12
~/Ircproxy/trio-ircproxy/trio-ircproxy.py** to run the app. Don’t forget to install the
requirements.txt with **pip3 install -r ~/Ircproxy/trio-ircproxy/requirements.txt**

Copyright License
=================

BSD Zero-Clause License Copyright (c) 2024, Master Sire GI Kenggi J.P. phd.
*ret. All rights reserved*. Please read *CODE_OF_CONDUCT.md* if you may, and see
file *LICENCE* for a short read if you plan on using Trio-Ircproxy.py to make
money or make changes. If you make changes, such as a Pull Request and I use
your code you accept the LICENSE that comes with the PR or other
**contribution.**

The web-server half of the project is available in another repo found at
**https://github.com/ashburry-trio/RoseMay** and runs with Flask on
**https://www.PythonAnywhere.com** servers. It is being developed in real-time at
**https://ashburry.pythonanywhere.com** or **https://www.myproxyip.com** page by 
page and has a long way to go. Once in awhile I update the repo with the web-site 
code which you can get working with minimal effort, even start your own web-site
based on RoseMay; if you require a login I would recommened letting me code the login
logic as it is tricky and difficult.

o end of document.

 
