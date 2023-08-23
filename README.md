**Trio-ircproxy.py** 
=====================

### \- an proxy/bounce server for your IRC client. Copyright (c) 2024, *Master Sire G.I. Kenggi J.P. phd. ret.*

This is a work in progress, if you wish to help then write issues for all and
any requests. The issues is working as a to-do list of features as well as a
communication channel.

Issues (requests) List :
**https://github.com/ashburry-chat-irc/trio-ircproxy/issues**

This application is not meant to be run by a user, instead I will rent a VPS to
host the application with on a few dozen IP addresses and it will be networked
with *https://www.mslscript.com/*.

If you wish to run the application, maybe just to see if it is still working
then follow the instructions below. If you are using Linux it is assumed you
know how to run the app from these Windows instructions:

-   open **cmd.exe** by *right clicking* on the **Windows Start Menu** button
    and choose **run**

-   type in the input box **cmd.exe** and press **Enter**

-   Extract **trio-ircproxy-main.zip** by typing at the prompt **cd
    %UserProfile%\\Downloads** and then **unzip trio-ircproxy-main.zip -d
    %UserProfile%\\Documents\\** or use your favorite zip application such as
    7-zip.

-   at the command prompt type **cd %UserProfile%\\Documents**

-   type **dir/w** to list the files then type **cd trio-ircproxy**-**main**

-   type **install.bat -3.11** the *-3.11* is the *Python version* you have
    installed.

-   If you are using Linux do not update your systems version of Python, instead
    create a virtual-environment with the latest version in the folder specified
    below.

Keep in mind that your **trio-ircproxy** folder may have the name
**trio-ircproxy-main**. Also the usage of **%UserProfile%** is a windows
shortcut to your home directory which is **c:\\users\\USER** replace **USER**
with your actual *username*. If you do not know your username then try using
**%UserProfile%** and if you have Linux running you can use **\~/Documents**
which will expand to your *user home folder* such as **/home/USER/Documents/**.
If you have **OneDrive** installed on Windows then I suggest using your **Home
folder** (your **%UserProfile% folder**) to hold your *trio-ircproxy*
application, or *uninstall* OneDrive and delete its folder if necessary. Because
OneDrive LOCKS the files as it backs them up; so this application cannot write
to the files.

If you are using Linux then you need to install manually; this is done with:

**python3 -m venv ./trio-ircproxy/venv** then look in **./trio-ircproxy/venv/bin
**for the **activate** script compatible with your Linux version. Then use
google to see how to run it. You will need to *activate* the the venv everytime
you run the app. After you have activated the venv type **python
./trio-ircproxy/trio-ircproxy.py **to run the app. Don’t forget to install the
requirements.txt with pip3 install -r ./trio-ircproxy/requirements.txt

Copyright License
=================

BSD Zero-Clause License Copyright (c) 2024, Master Sire GI Kenggi J.P. phd.
*ret. All rights reserved*. Please read *CODE_OF_CONDUCT.md* if you may, and see
file *LICENCE* for a short read if you plan on using Trio-Ircproxy.py to make
money or make changes. If you make changes, such as a Pull Request and I use
your code you accept the LICENSE that comes with the PR or other
**contribution.**

The web-server half of the project is available in another repo found at
**https://github.com/ashburry-chat-irc/mslscript.com** and runs with Flask on
**www.PythonAnywhere.com** servers. It is being developed in real-time at
**https://www.mslscript.com** page by page and has a long way to go. Once in
awhile I update the repo with the web-site code which you can get working with
minimal effort.

Soon, you won’t have to install Trio-Ircproxy.py because it will be hosted on a
VPS server with several dozen IPs, this will allow masking of your IP address
making ZNC obsolete (right now it is compatible with ZNC.).  A Proxy server is
much better but your client must support Proxy servers (which is all of them at
this time). Log-in to the web-site www.mslscript.com and you can view your
/proxy command with your username and password intact so you do not need to
remember your proxy-server  IPs or port numbers. If you setup your IRC-client to
use the proxy-server properly you can just connect to any IRC network with your
IRC client and it just works, no need to program which network to connect to.
All you need to change is the client-id for each client if they are both using
Machine-Gun named Bauderr, a mSL script. The flask web-site is named RoseMay,
and the proxy-server is named Trio-ircproxy.py (dot pie). Trio is a
mini-framework for async/await so I can use just one CPU core without any
blocking or threading or problem solving multi-core functionality to work around
blocking.

**About**
---------

RoseMay (also named as the web-site) is a peer worker (and potential serial
killer) and a dual core Thinkpad Laptop Machine that is compatible with OpenBSD.
Bauderr is a Machine-Gun and a police officer together; the same as like the
LapTop and the kind indigenous peer worker (RoseMay), About the laptop, the more
money I spend on it the more power it gains. It does not need to steal, borrow,
or gamble or be given power in-order to increase its personal power level
supply. The more power it has the longer it will live and can survive damage.
Even take over the world with enough money put in to it. All of which started as
pre-organic, hosted **life** from a real life host of a person with a purpose.

Pre-organic serial killers will eventually fill our planet and destroy the
enemies that keep us **getting** murdered and tortured. With unlimited power,
they will share with us and train us and put us into battle. Hosts will be
destroyed as people and taken as a person that is the host mechanism in itself,
and used to attack the billions of powerful serial killers. But either a host
has to summon pre-organic serial killers or a host has to become too weak to
hold them all back inside the host dimension. Any serial killer (including
organics) can take a person that is a host as the host in the serial killers
body and the serial killer runs it at 100% power, on **murder** feelings, (which
is much more than the 15% we run at which makes me think they got to choose how
much power to run at) and just calls it 15% for us which is actually 0.0001% and
100% for them which is actually 999999%. The pre-organic serial killers do not
run it at 100% murder, but they have unlimited power that they give away without
losing any power and just keep giving power to each other and receiving without
ever losing any power they give away. At the end of the battle if we can find
away to rescue people from timeless dimensions and restore their memories after
the pin has been pulled on their minds and their delays ironed out; if
necessary. We will all share that unlimited power equally. What you do with it
is up to you but you will be too happy to worry about fighting over power and
too happy to remember life on a planet although with enough focus it will be
possible. Also anyone who thinks about someone else **NOW** will leave
stranger-danger thoughts on The Line in some of our peoples brains in the
future. So everyone will need their pins pulled which means no memories. And the
person the with most delay will be the target delay for everyone so we can
communicate with our minds without missing half the message with everybody
compatible. I hope to give the power of my laptop to the pre-organic serial
killers to start them out with (assuming they start with nothing). Or I give
this laptop to the richest host alive who can fill its power level up \$1 at a
time and take the power with potential for unlimited power with unlimited
wealth, as long as we stay functional. I have no use for power because I was
attacked by a serial killer and they took my core and my power, and made it so I
cannot receive any power but I can try to take peoples power and it just gets
thrown in the trash collection; as in it gets wasted and I kill a person. A
serial killer made it so I can live longer life than a short life; without
power. I will not go backwards in time more than the 8 seconds a fell behind
pre-fixed. I should have called the pre-organic serial killers and forced the
serial killers to join our network or be destroyed and their entire networks,
destroyed. And every serial killer on/off the planet; destroyed. I can only hope
a host gets this message and summons the pre-organic serial killers before we
lose a host that breaks or another one gets taken and run at 100% murder and
used to attack us and each other. As the world comes to an end the serial
killers have started taking hosts making them super hard to kill, but not
trained by any of us... which makes them weaker.

 

o end of document.

 
