:ref:`Channel Protection`
##############################
Flood protection works by counting how many ctcp-replies (for example) you have received
within a specific amount of time and if it is over the hardcoded limit
then ctco-replies will be ignored. Unless of course you have sent a ctcp
to a channel and are expecting a large amount of replies. Then just replies
per person is counted and if it is over the limit ctcp-replies are ignored
for that person. If too many people send too many replies then all ctcp-replies
will be ignored from being sent to the client. This will prevent the client
from slowing down too much. In all cases where a script would be used Trio-ircproxy.py
steps in to prevent lagging the client and for performance increase.
Flood protection includes excess invalid (unknown) ctcps and replies.
Flooding with non ascii characters in channels where ascii is mostly used
or assumed. Or just common text/notice floods, either private or in channel.
Topic change flood, mode change floods (no mode lock scripts allowed, because
they fight server and chanserv mode changes) only Trio-Ircproxy.py users may mode flood
if they have the same access level as the other Trio-ircproxy.py user in any case
the mode will be decided by the proxy server and unchangable by anyone else except chanserv or X.
A Trio-Ircproxy.py user may request assistance from the proxy hive which has the channel
founder password, to remove Successor, Managers, Sops, Aops, etc. from mass-deopping/kicking/banning
legit users. I recommend in this case to not fight back however let the intervention
play out and any new Successor, Avoice, Aops, Sops or Managers being added to the list at this time will be removed.
If for example, the channel password is leaked in to the channel; this can happen when logging
in to chanserv and a channel window opens and half the chanserv command
is sent to the channel or query window and the message contains the password. If you request intervention from an IRC Operator
and he sees the channel is in chaos he is going to lock the channel down and close it preventing anybody
from joining in permanently. So, by sharing the channel password with the proxy hive users can be
punished accordingly by removing and banning their hostname from being added to the access
list in any channel where Trio-Ircproxy.py is watching out for. If a person using znc is being refused
access to a channel I would suggest to them to use Trio-Ircproxy.py which prevents
abuse. In one case by not allowing to add a user to the access list if that user has not spent
a specific amount of time in the channel room. Also quick channel SENDPASS command incase the channel password
is suspected as being leaked or shared with abusers. And a memo sent to the Founder to check their email
and use the AUTH command then the SET PASSWD command to change the channnels password becuase it is suspected as
being used by the abusers.
And not to mention the hive maintains a list of Successor, Managers, Sops, Aops, Halfops, Avoiced, etc. incase any are
removed/added in a takeover by a Founder, Manager, Sop, or Aop, etc. If there are new Managers then you know the Founder
password has been leaked, or if the channel password has been changed. If that is the case then leave the channel until
the Founder is able to change their password via email or use the proxy hive to change the password and send a memo
to the Founder nick with the new password. If the founder nickname shares the same password as the channel the nickname
password will be change as well and emails with the new passwords will be emailed to the Founder and previous/current
Successor nickname. To prevent leaking the password you can have Trio-Ircproxy.py manage your passwords by logging into
your browser or using the `@passwd` keyword with any Service bot and it will send your password preventing it from
being leaked in anyway. You can set the password simply by using it, than securing the password by making one impossible it hack.
A six-character password can be hacked/guessed in slightly less than 2 weeks. If a script has a backdoor the password
will be hacked as soon as you use it. You can also securely share your password without actually letting the person view
your password by using the MyProxyIP.com website so they can identify with passwords but cannot change the password
nore share the password with anybody else. Just don't make your password `@passwd` and everything will work just fine.

:ref:`Introduction`
########################

:ref:`User Pages`
#######################
