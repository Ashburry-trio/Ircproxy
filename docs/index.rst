.. |date| date::
.. |time| date:: %H :%M

Today's date is |date|    year/month/day.

This document was generated on |date| at |time|.

Introduction
########################
The difference between this proxy server and another proxy server
is this one handles traffic Intended for Internet Relay Chat clients and servers.
Trio-Ircproxy.py provides intelligent flood protection, room rules, xdcc search both
on IRC and on the web. A casino which can be played on the web or on IRC; it is very 
simple, yet fun. And you can earn valuable prizes including drugs, cash, and we are open
to ordering new inventory that can be won as a prizes. The most expensive game is $2 
and the inexpensive games are 5 cents. You can still win big on the 5 cent games. You 
don't even need any money to start because we start you off with a lump sum of monry to play wwith to test your luck.
I wish you best of luck while using Trio-Ircproxy.py. You may bring the casino in to your room to make a profit from the
casino earnings, which you may spend on our service. And btw, did I mention the incredible knock down on pricing for
the gifts; that's right, get an a ounce of Crystal-Meth for $60. And remember, stay safe.

User Pages
######################
User pages are web-pages on the www.MyProxyIP.com/user/<username> web-site
where stats are kept about the user such as /whois information but over a larger period of time.
You may keep private logs if up to 5000 lines per chat room or private.
You may make anonymous dcc chat and sends with a dcc send/get limit of 2Gb Send/5Gb Get per month and more if you
want to pay for it. Here at MyProxyIP.com we have ways of making you money, $300 can change your life.
You can turn that in to $1,000 in just few days delivery time. And even larger gains if you have more
money you can earn up to 12k. No saying its legit, not saying its not-legit. But playing at this casino the game for
prizes only you can win some wicked shit for 1/3rd the street cost. This is because you have to spend money and
play your luck.


Channel Protection
##############################
Flood protection works by counting how many ctcp-replies (for example) you have received
within a specific amount of time and if it is over the hardcoded limit
then ctco-replies will be ignored (not sent to the client). Unless of course you have sent a ctcp
to a channel and are expecting a large amount of replies. Then just replies
per person is counted and if it is over that limit, ctcp-replies are ignored
for that person. If too many people send
too many replies then all ctcp-replies will be ignored by not sending to the client.
This will prevent the client from slowing down too much, scripts cannot compete in speed with a well debugged Python3
app.
In all cases where a script would be used, Trio-ircproxy.py steps in to prevent a lagging client from a
performance decrease trying to run scripts which may appear to be fast but it is just an illusion of UX performance
tricks. And other scripts are just as slow so there is no real comparison to what speed is like in the IRC world.
Flood protection includes excess invalid (unknown) ctcps and replies.
Flooding with non ascii characters in channels where ascii is mostly used
or assumed. Or just common text/notice/action floods, either private or in channel.
Topic change flood, mode change floods (no mode lock scripts allowed, because
they fight server-mode changes, chanserv, or X bot, and part of flooding a channel is getting it on the netsplit
and flooding deop, ban, topic, and mode changes on the split server where they can gain ops in to room because everyone
else is on the other side of the netsplit. You can turn on `fight-back` mode where if anyone with a lower access level
deops, kicks, bans your nick, they will be met with an access remove command. It is good to have a founder sit in the
channel 24/7 to prevent mass-deops and mass-kicks. If you are going tio be away for awhile just use the /gone command
and you will be given a grace time of 30+ days before your account is removed. Just use /gone-back to mark yourself as
being back from your vacation. The only way to prevent your channel from continuously being attacked is to watch who
you add to your OP list and keep channel modes secure. When it doubt clear the HOP, AOP, SOP, lists respectively
until the flooding stops. With a single bot from the Trio-Ircproxy.py hive order can be restored by simply removing all
ops from the access list then mass-kicking the flood bots. An ACCESS WHY command will be sent for each op and anbody
who added that op to the access list will have their access removed aswell.