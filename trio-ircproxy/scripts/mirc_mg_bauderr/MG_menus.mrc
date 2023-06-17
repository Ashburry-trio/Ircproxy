;TODO add all menu item separators, .-, in the remotes menus; not the popups.ini
; /set_show_away 1 = notice 2 = private message 0 = off

alias no_script_file {
  echo >> $nofile($script)
}
on *:start: {
  unset %bde_temp*
}
raw 18:*: {
  if ($1- == :motd.mslscript.com motd.mslscript.com online) {
    set $varname_cid(trio-ircproxy,in_use) = $true
  }
}
on *:quit: {
  if ($nick == $me) { 
    unset $varname_cid(trio-ircproxy.py, active)
    unset $varname_cid(trio-ircproxy.py, admin)     
  }
}
alias onotice-script {
  var %room = #$$input(Enter a room name to send op-notice to:,eygbqk60m,enter a room name to send op-notice to,select a room,$chan(1),$chan(2),$chan(3),$chan(4),$chan(5),$chan(6),$chan(7),$chan(8),$chan(9),$chan(10))
  if (%room == #select a room) { return }
  %room = $gettok(%room,1,32)
  var %msg = $$input(Speak your notice to all chan-ops in %room $+ :,eygbqk60,Speak your notice to all chan-ops in %room,:: : MG script : .)
  /onotice %room %msg
}
alias omsg-script {
  var %room = #$$input(Enter a room name to send op-notice to:,eygbqk60m,enter a room name to send op-notice to,select a room,$chan(1),$chan(2),$chan(3),$chan(4),$chan(5),$chan(6),$chan(7),$chan(8),$chan(9),$chan(10))
  if (%room == #select a room) { return }
  %room = $gettok(%room,1,32)
  var %msg = $$input(Enter your message to all chan-ops in %room $+ :,eygbqk60,Enter your message to all chan-ops in %room,:: : MG script : .)
  /onotice %room %msg
}

alias parted_rooms {
  if ($1 isin begin end) { return }
  if ($chan($1).status == kicked) { return $chan($1) (kicked) : join $chan($1) }
  else { return $null }
  if ($1 == $chan(0)) { return }
}
alias style_show_away_not {
  if ($status != connected) || (!$network) { return $style(3) }
  if ($varname_global(show_away,blank).value == 0) { return $style(3) }
}
alias style_show_away_note {
  if ($status != connected) || (!$network) { return }
  if ($varname_global(show_away,blank).value == 1) { return $style(3) }
}
alias style_show_away_priv {
  if ($status != connected) || (!$network) { return }
  if ($varname_global(show_away,blank).value == $null) { set $varname_global(show_away,blank) 2 }
  if ($varname_global(show_away,blank).value == 2) { return $style(3) }
}

alias style_show_away {
  return $iif($style_show_away_priv $+ $style_show_away_note,$style(1))
}
alias set_show_away {
  if ($1 <= 2) && ($1 >= 0)  { set $varname_global(show_away,blank) $1 }
}
alias advertise-chan {
  if ($status != connected) { return }
  if ($chan != $null) { return this channel }
}
alias advertise-in-channel {
  if ($status != connected) { return }
  if ($chan(0) > 0) { return in channel }
}
alias advertise-chan-00 {
  if ($status != connected) { return }
  if ($chan(1) != $null) { return $chan(1) }
}
alias advertise-chan-01 {
  if ($status != connected) { return }
  if ($chan(2) != $null) { return $chan(2) }
}
alias advertise-chan-02 {
  if ($status != connected) { return }
  if ($chan(3) != $null) { return $chan(3) }
}
alias advertise-chan-03 {
  if ($status != connected) { return }
  if ($chan(4) != $null) { return $chan(4) }
}
alias advertise-chan-04 {
  if ($status != connected) { return }
  if ($chan(5) != $null) { return $chan(5) }
}
alias advertise-chan-05 {
  if ($status != connected) { return }
  if ($chan(6) != $null) { return $chan(6) }
}
alias advertise-chan-06 {
  if ($status != connected) { return }
  if ($chan(7) != $null) { return $chan(7) }
}
alias advertise-chan-07 {
  if ($status != connected) { return }
  if ($chan(8) != $null) { return $chan(8) }
}
alias advertise-chan-08 {
  if ($status != connected) { return }
  if ($chan(9) != $null) { return $chan(9) }
}
alias advertise-chan-09 {
  if ($status != connected) { return }
  if ($chan(10) != $null) { return $chan(10) }
}
alias advertise-this-connection {
  if ($status != connected) { return }
  if ($chan(0) == 0) { return }
  return all chans on this connection
}
alias advertise-network {
  if ($network == $null) { return }
  return chans on network $network
}
alias advertise-this-client {
  return everywhere on this client
}
alias advertise-user {
  return all proxy user $varname_cid(trio-ircproxy.py, is_user).value
}
alias block {
  if (strip($1) == $null) { return }
  return $chr(91) $+ $1- $+ $chr(93)
}
alias -l style_net_chan_link {
  if (!$chan) { return }
  if ($varname_global(network-link,$chan).value) { return $style(1) }
}
menu Status,Channel {
  $chr(46) $chr(58) M&achine Gun $str($chr(58),2) $chr(58)
  .$style_proxy $chr(46) $chr(58) describe mg $str($chr(58),2) $chr(58)
  ..$advertise-chan : /describe $chan is using Machine Gun mSL script named Bauderr. use ctcp version/script/source for more info.
  ..$advertise-in-channel
  ...$advertise-chan-00 : /bauderr-advertise --chan $chan(1)
  ...$advertise-chan-01 : /bauderr-advertise --chan $chan(2)
  ...$advertise-chan-02 : /bauderr-advertise --chan $chan(3)
  ...$advertise-chan-03 : /bauderr-advertise --chan $chan(4)
  ...$advertise-chan-04 : /bauderr-advertise --chan $chan(5)
  ...$advertise-chan-05 : /bauderr-advertise --chan $chan(6)
  ...$advertise-chan-06 : /bauderr-advertise --chan $chan(7)
  ...$advertise-chan-07 : /bauderr-advertise --chan $chan(8)
  ...$advertise-chan-08 : /bauderr-advertise --chan $chan(9)
  ...$advertise-chan-09 : /bauderr-advertise --chan $chan(10)
  ..$advertise-this-connection : /bnc_msg advertise-connection
  ..$advertise-network : bnc_msg --advertise-network-with-bauderr
  ..$advertise-this-client : /scon -a /ame is using Machine Gun mSL script named Bauderr. use ctcp version/script/source for more info.
  ..$advertise-user : bnc_msg advertise-username-with-bauderr
  ..everywhere possible : bnc_msg --advertise-everywhere-with-bauderr
  -
  &room functions
  .&chanserv
  ..$identify_here_popup : /bnc_msg identify-chanserv $$chan 
  ..$popup-identify-founder-list
  ...$submenu($identify_chans_popup($1))
  .topi&c history
  ..$submenu($topic_history_popup($1))
  ..-
  ..$iif(($eval($var($varname_global(topic_history_ $+ $chan,*),1),1) == $null || (!$chan)),$style(3)) erase topic history for channel : unset $varname_global(topic_history_ $+ $chan,*) | eecho -sep topic history cleared for room $chan
  ..$iif(($eval($var($varname_global(topic_history_*,*),1),1) == $null),$style(3)) erase entire topic history : unset $varname_global(topic_history_*,*) | eecho -sep topic history for ALL channels is cleared
  ..-
  ..$iif((!$chan),$style(2)) add this topic to history : topic_history_add $chan $chan($chan).topic
  ..-
  ..$iif(($varname_global(topic-history-off,blank).value == $true),$style(1)) turn OFF topic history : set $varname_global(topic-history-off,blank) $iif(($varname_global(topic-history-off,blank).value == $true),$false,$true)
  .-
  .[&allow prevention]
  ..$style_allow_ascii &allow ascii-art
  ...$style_allow_paste &allow paste 25 lines : set_allow_room_paste
  ...$style_allow_long_word &allow long words : set_allow_room_long_word
  ...$style_allow_line &allow long lines : set_allow_room_long_line
  ...$style_allow_repeat &allow repeat 6x : set_allow_room_repeat
  ...$style_allow_rand_text [&allow random text] : set_allow_room_random_text
  ...-
  ...$style_allow_ascii allow ascii-art (everything) : set_allow_asciiart
  ; menu
  ..$style_bad_script_menu &allow bad scripts
  ...$style_bad_script allow bad scripts : set_allow_bad_script
  ...$style_bad_script_warn warning : set_allow_bad_script_warn
  ...$style_bad_script_ban [2hr ban] : set_allow_room_bad_script_ban
  ...-
  ...open bad script list : open_bad_script
  ; menu
  ..$style_allow_rand_nick &allow random nickname : set_allow_rand_nick
  ..$style_allow_clone &allow clone 10x : set_allow_room_clone
  ..-
  ..$style_allow_share [&allow file sharing] : set_allow_room_file_share
  ..$style_allow_idle [&allow idle 25+ minutes] : set_allow_room_idle
  ..$style_allow_binart [&allow bin-art && non-english] : set_allow_room_binart
  ; menu
  ..$style_allow_bad_word [&allow bad words]
  ...$style_allow_bad_word_off do not allow bad words : set_allow_room_badword
  ...-
  ...open bad word list : open_bad_word
  ; menu
  ..$style_allow_room_name [&allow advertising other #room-names]
  ...$style_allow_room_name_off do not allow : set_allow_room_name
  ...-
  ...open allowed list : open_allowed_room
  ; menu
  ..$style_allow_url [&allow speaking $+(https,$chr(58),//URLs,]) 
  ...$style_allow_url_off do not allow : set_allow_room_url
  ...-
  ...open always allowed-url list : open_allowed_url
  ; menu
  ..$style_bad_chan [&allow bad room]
  ...$style_bad_chan_off do not allow : set_allow_room_bad_chan
  ...-
  ...open bad room list : open_bad_chan
  ..-
  ..$style_allow_non_default set non-defaults to allow : set_allow_room_non_default $chan $varname_global(allow_room_non_default,$network $+ $chan).value
  ..$style_allow_default [set defaults to allow] : set_allow_room_default
  ; menu
  .[ir&c oper scan]
  ..-
  ..$iif(($chan == $null),$style_proxy) scan here : /operscan $chan
  ..$style_proxy scan everywhere : /operscan
  ..-
  ..s&can on join
  ...$menu_enable_oper_scan switch OFF scanning : disable_oper_scan
  ...-
  ...$oper_scan_net switch ON for this network : toggle_oper_scan_net
  ...$oper_scan_cid switch ON for this connection id (temporary) : toggle_oper_scan_cid
  ...-
  ...$oper_scan_cid_chan switch ON for this channel/connection id (temporaryp) : toggle_oper_scan_cid_chan
  ...$oper_scan_net_chan [switch ON for this channel/network] : toggle_oper_scan_net_chan
  ...$oper_scan_client [switch ON for this irc-client] : toggle_oper_scan_client

  .$style_net_chan_link network channel link 
  ..$style_link_on turn on here : {
    if ($varname_global(network-link,$chan).value > 0) { set $varname_global(network-link,$chan) 0 | status_msg set channel-link $chan off }
    else { set $varname_global(network-link,$chan) $cid | status_msg set channel-link $chan $cid }
  }
  ..-
  ..in&fo : /script_info -chan_link
  .$style_annc_urls describe urls : annc_urls_toggle
  ..-
  ..info : script_info -urls
  .-

  .$style_auto_ial [&auto update ial] : toggle_auto_ial

  &trio-ircproxy.py
  .&web-site
  ..&describe home-chan/user
  ..&change URL
  ..&change username/password
  ..-
  ..visit your home-page : bnc_msg send-home-page
  ..-
  ..in&fo : /script_info -identity
  .-

  ; Keep track of the IP and PORT in use so you know where to send the shutdown command to
  .&start and stop
  ..&start trio-ircproxy.py : /run $varname_glob(python,none).value $scriptdir..\..\trio-ircproxy.py
  ..-
  ..$style-proxy-shutdown &shutdown trio-ircproxy.py : /proxy-shutdown
  .command line
  ..run proxy : run $scriptdir..\..\..\runproxy.bat | eecho if there is an error the cmd.exe window will close automatically.
  ..-
  ..$iif(($exists($scriptdir..\..\venv)),$style(3)) &install : run $qt($scriptdir..\..\..\install.bat)

  .-
  .listen with ip
  ..$iif(($varname_glob(bind-ip).value == private),$style(1)) 127.0.0.1 (private/this computer only) : set $varname_global(bind-ip) private
  ..$iif(($varname_glob(bind-ip).value == global),$style(1)) [0.0.0.0 (public/local network)] : set $varname_global(bind-ip) global
  ..-
  ..info : script_info -listen

  .u&se port numbers
  ..$style(1) change $block(BNC $varname_glob(use-port,proxy).value) : {
    var %pp = $$?="enter a port number for your proxy server: [4321]:"
    set-service-port %pp
  }
  ..$iif(($varname_glob(use-port,proxy).value == 4321),$style(3)) [4321] : { set-service-port 4321 }

  ..-
  ..info : script_info -port
  .-
  .running status : /bnc_msg status
  &connect irc
  .last used : /server
  .-
  .with proxy 
  ..192.168.0.17 4321 : /proxy on | var %net = $iif(($network),$network,$$?="enter network name:") | /server $$server(1, %net) $+ : $+ $remove($server(1, %net).port,+) 
  .with vhost
  ..38.242.206.227 7000 : /proxy off | var %net = $$?="enter network name:") | /server 38.242.206.227:7000 $$?="enter your username:" $+ / $+ %net $+ : $+ $$?="enter your password:"
  ..192.168.0.17 +6697 : /proxy off | var %net = $iif(($network),$network,$$?="enter network name:") | /server 192.168.0.17:+6697 $$?="enter your username:" $+ / $+ %net $+ : $+ $$?="enter your password:"
  .-
  .without proxy nor vhost : /proxy off | /server $server(1, $iif(($network),$network,$$?="enter network name:"))
  ; command history
  ;.xcdcc send #899 : /msg [MG]-MISC|EU|S|RandomPunk xdcc send #899
}
alias -l style_link_on {
  if (!$chan) { return $style(2) }
  if ($varname_global(network-link,$chan).value == 1) { return $style(1) }

}
alias -l BAUDERR-ADVERTISE {
  if ($1 == --chan) {
    describe $$2 is using Machine Gun mSL script named Bauderr. use ctcp version / script / source for more info.
  }
}
alias style_auto_ial {
  if ($varname_global(auto_ia1,blank).value == $true) || ($varname_global(auto_ia1,blank).value == $null) { return $style(1) }
}
alias toggle_auto_ial {
  set $varname_global(auto_ia1,blank) $iif($1 != $null,$1,$iif(($varname_global(auto_ia1,blank).value == $true || $varname_global(auto_ia1,blank).value == $null),$false,$true))
}
alias -l style_annc_urls {
  return $iif(($varname_cid(annc_urls,blank).value),$style(1))
}
alias -l annc_urls_toggle {
  set $varname_cid(annc_urls,blank) $iif(($varname_cid(annc_urls,blank).value),$false,$true)
}

alias play-sound-history {
  if ($1 isin begin end) { return asdf }
  if ($1 == 16) { return }
  var %fn = $varname_global(sound-history,$1).value
  if (!%fn) { return }
  return $nopath(%fn) : play-sound $eval($iif($active == $chan || $active == $nick,$ifmatch,$gettok($$?="enter a room or nickname to play to:",1,32)),0) %fn
}
alias play-sound {
  var %file = $qw($2-), %fn
  if (!$exists(%file)) { return }
  var %n = 1, %empty
  while (%n < 16) {
    %fn = $varname_global(sound-history,%n).value
    if (%fn) && ($exists(%fn) == $false) { var %fn | unset $varname_global(sound-history,%n) }
    elseif (%fn == %file) { %empty = skip | break }
    if (!%fn) && (!%empty) { %empty = %n }
    inc %n
  }
  if (%empty == $null) {
    if ($varname_global(sound-history,last-n).value == $null) { set $varname_global(sound-history,last-n) 1 }
    set $varname_global(sound-history,last-n) $calc($varname_global(sound-history,last-n).value + 1)
    if ($varname_global(sound-history,last-n).value > 15) { set $varname_global(sound-history,last-n) 1 }
    set $varname_global(sound-history,$varname_global(sound-history,last-n).value) %file
  }
  else { if (%empty != skip) { set $varname_global(sound-history,%empty) %file } }
  var %m = is playing a sound * 76,1 E n j o y!   *
  if (C isin $chan($1).mode) { %m = $strip(%m) }
  sound $1- %m
  if ($varname_temp(soundfile-message,blank).value != $true) {
    set $varname_temp(soundfile-message,blank) $true
    .timersoundfile-message -o 1 $calc(60 * 12) /set $varname_temp(soundfile-message,blank) $false
  }
  else { return }
  echo (for other ppl to listen to the sound file they paste) ! $+ $me $nopath(%file)  (in channel or private message. use /splay stop)
}
alias -l oper_scan_client {
  if ($varname_global(oper-scan-client,blank).value == $true) { return $style(1) }
}
alias -l toggle_oper_scan_client {
  set $varname_global(oper-scan-client,blank) $iif($1 isin $!true$false,$1,$iif($varname_global(oper-scan-client,blank).value == $true,$false,$true))
}
alias -l open_allowed_url {
  var %fn = $qw($scriptdir..\website_and_proxy\settings\allowed-url-list.txt)
  if ($exists(%fn) == $false) { write -c %fn }
  run %fn

}
alias -l open_bad_word {
  var %fn = $qw($scriptdir..\website_and_proxy\settings\bad-word-list.txt)
  if ($exists(%fn) == $false) { write -c %fn }
  run %fn
}
alias -l open_bad_chan {
  var %fn = $qw($scriptdir..\website_and_proxy\settings\bad-chan-list.txt)
  if ($exists(%fn) == $false) { write -c %fn }
  run %fn
}
alias -l open_allowed_room {
  var %fn = $qw($scriptdir..\website_and_proxy\settings\allowed-room-names.txt)
  if ($exists(%fn) == $false) { write -c %fn }
  run %fn
}
alias -l style_bad_chan_off {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_chan,$network $+ $chan).value == $false) { return $style(1) }
}
alias -l style_bad_chan {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_chan,$network $+ $chan).value == $true) || ($varname_global(allow_bad_chan,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_default {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_default,$network $+ $chan).value == $true) || ($varname_global(allow_room_default,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_repeat {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_repeat,$network $+ $chan).value == $true) || ($varname_global(allow_room_repeat,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_bad_script_ban {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $null) && ($varname_global(bad_script_warn,$network $+ $chan).value == $null) && ($varname_global(allow_bad_script,$network $+ $chan).value == $null) { 
    set $varname_global(allow_bad_script_ban,$network $+ $chan) $true
    return $style(3)
  }
  if ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $true) || ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $null) { return $style(3) }
}
alias -l style_bad_script_warn {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $null) && ($varname_global(bad_script_warn,$network $+ $chan).value == $null) && ($varname_global(allow_bad_script,$network $+ $chan).value == $null) { return }
  if ($varname_global(bad_script_warn,$network $+ $chan).value == $true) || ($varname_global(bad_script_warn,$network $+ $chan).value == $null) { return $style(3) }
}
alias -l style_bad_script_menu {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $null) && ($varname_global(bad_script_warn,$network $+ $chan).value == $null) && ($varname_global(allow_bad_script,$network $+ $chan).value == $null) { return }
  if (($varname_global(allow_bad_script,$network $+ $chan).value == $true) || ($varname_global(allow_bad_script,$network $+ $chan).value == $null)) || ($varname_global(bad_script_warn,$network $+ $chan).value == $true) { return $style(1) }
}
alias -l style_bad_script {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_script_ban,$network $+ $chan).value == $null) && ($varname_global(bad_script_warn,$network $+ $chan).value == $null) && ($varname_global(allow_bad_script,$network $+ $chan).value == $null) { return }
  if (($varname_global(allow_bad_script,$network $+ $chan).value == $true) || ($varname_global(allow_bad_script,$network $+ $chan).value == $null)) { return $style(3) }
}

alias -l style_bad_chan {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_chan,$network $+ $chan).value == $true) || ($varname_global(allow_bad_chan,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_url {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_url,$network $+ $chan).value == $true) || ($varname_global(allow_room_url,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_url_off {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_url,$network $+ $chan).value == $false) { return $style(1) }
}
alias -l style_allow_room_name {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_name,$network $+ $chan).value == $true) || ($varname_global(allow_room_name,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_room_name_off {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_name,$network $+ $chan).value == $false) { return $style(1) }
}

alias -l style_allow_binart {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_binart,$network $+ $chan).value == $true) || ($varname_global(allow_room_binart,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_bad_word {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_bad_word,$network $+ $chan).value == $null) || ($varname_global(allow_bad_word,$network $+ $chan).value == $true) { return $style(1) }
}
alias -l style_allow_bad_word_off {
  if (!$network) || (!$chan) { return }
  if ($varname_global(allow_bad_word,$network $+ $chan).value == $false) { return $style(1) }

}
alias -l style_allow_idle {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_idle,$network $+ $chan).value == $true) || ($varname_global(allow_room_idle,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_share {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_sharing,$network $+ $chan).value == $true) || ($varname_global(allow_room_sharing,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_clone {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_clone,$network $+ $chan).value == $true) || ($varname_global(allow_room_clone,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_rand_nick {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_rand_nick,$network $+ $chan).value == $true) || ($varname_global(allow_rand_nick,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_long_word {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_long_word,$network $+ $chan).value == $true) || ($varname_global(allow_long_word,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_line {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_long_line,$network $+ $chan).value == $true) || ($varname_global(allow_long_line,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_paste {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_paste,$network $+ $chan).value == $true) || ($varname_global(allow_room_paste,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_non_default {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(allow_room_non_default,$network $+ $chan).value == $true) || ($varname_global(allow_room_non_default,$network $+ $chan).value == $null) { return $style(1) }
}
alias -l style_allow_rand_text {
  if (!$network) || (!$chan) { return $style(2) }
  if (($varname_global(allow_rand_text,$network $+ $chan).value == $true) || ($varname_global(allow_rand_text,$network $+ $chan).value == $null)) { return $style(1) }
}
alias -l style_allow_ascii {
  if (!$network) || (!$chan) { return $style(2) }
  if (($varname_global(allow_rand_text,$network $+ $chan).value == $true) || ($varname_global(allow_rand_text,$network $+ $chan).value == $null)) && (($varname_global(allow_room_paste,$network $+ $chan).value == $true) || ($varname_global(allow_room_paste,$network $+ $chan).value == $null)) && (($varname_global(allow_long_line,$network $+ $chan).value == $true) || ($varname_global(allow_long_line,$network $+ $chan).value == $null)) && $&
    (($varname_global(allow_long_word,$network $+ $chan).value == $true) || ($varname_global(allow_long_word,$network $+ $chan).value == $null)) && (($varname_global(allow_room_repeat,$network $+ $chan).value == $true) || ($varname_global(allow_room_repeat,$network $+ $chan).value == $null)) { return $style(1) }
}

alias -l get_bool {
  if (!$network) || ($left($1,1) != $chr(35)) || (!$2) { halt }
  var %bool
  if ($3 == $null) {
    if ($varname_global($2,$network $+ $1).value == $null) { 
      var %bool = $false
      set $varname_global($2,$network $+ $1) $false
    }
    elseif ($varname_global($2,$network $+ $1).value != $true) { var %bool = $true }
    else { var %bool = $false }
  }
  else {
    if ($2 == on) || ($2 == yes) || ($2 == true) || ($2 == $true) { var %bool = $false }
    elseif ($2 == off) || ($2 == no) || ($2 == false) || ($2 == $false) { var %bool = $true }
    elseif {%bool == $null) { var %bool = $true }
    else { var %bool = $false }
  }
  if ($3 != $null) { set $varname_global($3,$network $+ $1) %bool }
  elseif ($2 != $null) { set $varname_global($2,$network $+ $1) %bool }
}
alias set_allow_room_binart {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_binart
  get_bool $1-
  if ($varname_global(allow_room_binart,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }

}
alias set_allow_rand_nick {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_rand_nick
  get_bool $1-
  if ($varname_global(allow_rand_nick,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}

alias set_allow_room_clone {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_clone
  get_bool $1-
  if ($varname_global(allow_room_clone,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_bad_script_ban {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_bad_script_ban
  get_bool $1-
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(bad_script_warn,$network $+ $1) $false }
  if ($varname_global(allow_bad_script,$network $+ $1).value == $true) { set $varname_global(bad_script_warn,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(bad_script_warn,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }
}
alias set_allow_bad_script_warn {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) bad_script_warn
  get_bool $1-
  if ($varname_global(bad_script_warn,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(bad_script_warn,$network $+ $1) $false }
  if ($varname_global(allow_bad_script,$network $+ $1).value == $true) { set $varname_global(bad_script_warn,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(bad_script_warn,$network $+ $1).value == $true) { set $varname_global(allow_room_default,$network $+ $1) $false }

}
alias set_allow_bad_script {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_bad_script
  get_bool $1-
  if ($varname_global(allow_bad_script,$network $+ $1).value == $true) { set $varname_global(bad_script_warn,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(bad_script_warn,$network $+ $1) $false }
  if ($varname_global(bad_script_warn,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(allow_bad_script,$network $+ $1).value == $true) { set $varname_global(allow_room_default,$network $+ $1) $false }

}

alias set_allow_room_badword {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_bad_word
  get_bool $1-
  if ($varname_global(allow_bad_word,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }
}
alias set_allow_room_non_default {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_non_default
  if ($varname_global(allow_room_non_default,$network $+ $1).value == $true) || ($varname_global(allow_room_non_default,$network $+ $1).value == $null) { 
    set_allow_asciiart_non_default $1 $false
    set $varname_global(allow_bad_script_ban,$network $+ $1) $true
    set $varname_global(allow_bad_script,$network $+ $1) $false
    set $varname_global(allow_rand_nick,$network $+ $1) $false
    set $varname_global(allow_room_clone,$network $+ $1) $false
    set $varname_global(allow_room_non_default,$network $+ $1) $false
  }
  else { 
    set $varname_global(allow_bad_script_ban,$network $+ $1) $false
    set $varname_global(allow_bad_script,$network $+ $1) $true
    set $varname_global(allow_rand_nick,$network $+ $1) $true
    set $varname_global(allow_room_clone,$network $+ $1) $true
    set_allow_asciiart_non_default $1 $true | set $varname_global(allow_room_non_default,$network $+ $1) $true 
  }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $true) || ($varname_global(allow_bad_script_ban,$network $+ $1).value == $null) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(bad_script_warn,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $true }
  if ($varname_global(bad_script_warn,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(allow_bad_script_ban,$network $+ $1) $false }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $true) { set $varname_global(allow_bad_script,$network $+ $1) $false | set $varname_global(bad_script_warn,$network $+ $1) $false }
  if ($varname_global(allow_bad_script_ban,$network $+ $1).value == $trueentire to) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_default {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_default
  get_bool $1-
  set $varname_global(allow_room_sharing,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_room_idle,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_bad_word,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_room_binart,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_room_name,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_room_url,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_bad_chan,$network $+ $1) $varname_global(allow_room_default,$network $+ $1).value
  set $varname_global(allow_rand_text,$network $+ $1) $true
}
alias set_allow_room_bad_chan {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_bad_chan
  get_bool $1-
  if ($varname_global(allow_bad_chan,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }
}
alias set_allow_room_repeat {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_repeat
  get_bool $1-
  if ($varname_global(allow_room_repeat,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_paste {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_paste
  get_bool $1-
  if ($varname_global(allow_room_paste,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_long_word {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_long_word
  get_bool $1-
  if ($varname_global(allow_long_word,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_long_line {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_long_line
  get_bool $1-
  if ($varname_global(allow_long_line,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}
alias set_allow_room_random_text {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_rand_text
  get_bool $1-
  if ($varname_global(allow_rand_text,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }

}
alias set_allow_asciiart {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_asciiart
  get_bool $1-
  set $varname_global(allow_rand_text,$network $+ $1) $true
  set $varname_global(allow_room_paste,$network $+ $1) $varname_global(allow_asciiart,$network $+ $1).value
  set $varname_global(allow_long_line,$network $+ $1) $varname_global(allow_asciiart,$network $+ $1).value
  set $varname_global(allow_long_word,$network $+ $1) $varname_global(allow_asciiart,$network $+ $1).value
  set $varname_global(allow_room_repeat,$network $+ $1) $varname_global(allow_asciiart,$network $+ $1).value
  if ($varname_global(allow_asciiart,$network $+ $1).value == $false) { set $varname_global(allow_room_non_default,$network $+ $1) $false }
}

alias set_allow_asciiart_non_default {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_asciiart
  if ($2 == $null) { return }
  set $varname_global(allow_asciiart,$network $+ $1) $2
  set $varname_global(allow_rand_text,$network $+ $1) $true
  set $varname_global(allow_room_paste,$network $+ $1) $2
  set $varname_global(allow_long_line,$network $+ $1) $2
  set $varname_global(allow_long_word,$network $+ $1) $2
  set $varname_global(allow_room_repeat,$network $+ $1) $2
  set $varname_global(allow_room_non_default,$network $+ $1) $2
}
alias SET_ALLOW_ROOM_FILE_SHARE {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_sharing
  get_bool $1-
  if ($varname_global(allow_room_sharing,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }
}
alias set_allow_room_idle {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_idle
  get_bool $1-
  if ($varname_global(allow_room_idle,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }
}
alias set_allow_room_url {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_url
  get_bool $1-
  if ($varname_global(allow_room_url,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }

}
alias set_allow_room_name {
  tokenize 32 $iif(($left($1,1) == $chr(35)),$1 $2,$chan $1) allow_room_name
  get_bool $1-
  if ($varname_global(allow_room_name,$network $+ $1).value == $false) { set $varname_global(allow_room_default,$network $+ $1) $false }

}
alias -l set-service-port {
  %pp = $remove($1-,[,])
  %pp = $remove(%pp,$chr(32))

  if (!$isnum(%p)) || (%p < 1) || (%p > 65535) { errecho invalid port number, port must be from 1 to 65535. | eecho port numbers between 1122 and 5000 are recommended. | return }
  set $varname_glob(use-port,proxy) %pp
  /writeini $scriptdir\..\www\www-server-config.ini %topic proxy-port %pp
  eecho restart Trio-IrcProxy.py for changes to take affect. Also, change your mIRC proxy settings.
}

alias menu_enable_oper_scan {
  if ($varname_cid(oper-scan-cid).value) { return }
  if ($chan && $varname_cid(oper-scan-cid-chan,$chan).value) { return }
  if ($network && ($varname_global(oper-scan-net,$network).value)) { return }
  if ($network && $chan && ($varname_global(oper-scan-net-chan,$+($$network,$$Chan)).value)) { return }
  if ($varname_global(oper-scan-client,blank).value) { return }
  return $style(1)
}

alias disable_oper_scan {
  set $varname_cid(oper-scan-cid) $false
  if ($network) { set $varname_global(oper-scan-net,$$network) $false }
  if ($chan) { set $varname_cid(oper-scan-cid-chan,$$chan) $false }
  if ($chan) && ($network) { set $varname_global(oper-scan-net-chan,$+($$network,$$Chan)) $false }
  set $varname_global(oper-scan-client,blank) $false
}
alias oper_scan_net_chan {
  if (!$network) || (!$chan) { return $style(2) }
  if ($varname_global(oper-scan-net-chan,$+($$network,$$Chan)).value) { return $style(1) }
}
alias toggle_oper_scan_net_chan {
  if ($network == $null) || (!$chan) { return }
  if (!$varname_global(oper-scan-net-chan,$+($$network,$$Chan)).value) {
    /set $varname_global(oper-scan-net-chan,$+($$network,$$Chan)) $true
  }
  else { /set $varname_global(oper-scan-net-chan,$+($$network,$$Chan)) $false }
}

alias -l oper_scan_cid_chan {
  if ($chan == $null) { return $style(2) }
  if ($varname_cid(oper-scan-cid-chan,$$chan).value) { return $style(1) }

}
alias -l toggle_oper_scan_cid_chan {
  if (!$varname_cid(oper-scan-cid-chan,$$chan).value) {
    /set $varname_cid(oper-scan-cid-chan,$chan) $true
  }
  else {
    /set $varname_cid(oper-scan-cid-chan,$chan) $false
  }
}

alias -l oper_scan_cid {
  if ($varname_cid(oper-scan-cid).value) { return $style(1) }

}
alias toggle_oper_scan_cid {
  if ($varname_cid(oper-scan-cid).value == $true) {
    /set $varname_cid(oper-scan-cid) $false
  }
  else {
    /set $varname_cid(oper-scan-cid) $true
  }
}

alias oper_scan_net {
  if ($network == $null) { return $style(2) }
  if ($varname_global(oper-scan-net,$$network).value) { return $style(1) }
}
alias toggle_oper_scan_net {
  if ($network == $null) { return }
  if (!$varname_global(oper-scan-net,$$network).value) {
    /set $varname_global(oper-scan-net,$$network) $true
  }
  else { /set $varname_global(oper-scan-net,$$network) $false }
}
alias style-proxy-shutdown {
  if ($varname_cid(using-bnc) != $true) { return $style(2) }

}
alias /proxy-shutdown {
  if ($varname_cid(using-bnc) == $true) {
    /raw proxy-shutdown NOW
  }
}
;-
; chanserv exists:
;-
alias -l identify_here_popup {
  if ($bool_using_proxy != $true) { return }
  if ($varname_global(identify-chanserv,$+($chan,-,$$network)).value == $chan) { return identify here }
}
;-
alias -l identify_chans_popup {
  if ($1 == begin) { return }
  if ($1 == end) { return }
  var %chan = $var($varname_global(identify-chanserv,$+(*,-,$$network)),$1)
  %chan = [ [ %chan ] ]
  if (%chan == $null) && ($1 == 1) { return no channels : eecho you have not identified as founder of channel(s) on this network ( $+ $network $+ ). $chr(124) eecho after you identify as an founder your channel will be listed in the menu. }
  return %chan : /bnc_msg identify-chanserv %chan
}
on *:quit: {
  if ($nick == $me) { unset $varname_cid(trio_ircproxy.py,active) }
}
alias status_usenick_pop {
  if (!$varname_cid(trio-ircproxy.py,active).value) { return $style(2) }
  if ($varname_glob(status-nick,none).value == $1) { return $style(1) }
}
alias bool_using_proxy {
  if ($varname_cid(trio-ircproxy.py,active).value) { return $true }
  return $false
}
alias style_proxy {
  if (!$varname_cid(trio-ircproxy.py,active).value) { return $style(2) }
}
on *:text:*:$chr(42) $+ status: {
  tokenize 32 $strip($1-)
  if ($1- == Trio-ircproxy.py active for this connection) { set $varname_cid(trio-ircproxy.py, active) $true }
  if ($1- == you are logged-in as Administrator) { set $varname_cid(trio-ircproxy.py, admin) $true }
  if ($4 != $null) && (*your username is ??* iswm $1-4) { set $varname_cid(trio-ircproxy.py, is_user) $4 }
  if ($1 == admin-nick) { set $varname_glob(admin-nick,none) $$2 }
  if ($1 == admin-smtp-email) { set $varname_glob(admin-smtp-email,none) $$2 }
  if ($1 == admin-smtp-hostname) { set $varname_glob(admin-smtp-hostname,none) $$2 }
  if ($1 == admin-smtp-server-name) { set $varname_glob(admin-server-name,none) $$2 }
  if ($1 == admin-smtp-user) { set $varname_glob(admin-smtp-user,none) $$2 }
  if ($1 == admin-smtp-password) { set $varname_glob(admin-smtp-password,none) $$2 }
  if (say-away == $1) && ($2 isin $true$false) { set $varname_glob(say-away,none) $2 }
  if (operscan-join == $1) && ($2 isin $true$false) { set $varname_glob(operscan-join,none) $2 }
  if ($1 == use-ports) { set $varname_global(use-port,proxy) $2 | set $varname_global(use-port,http) $3 }
  if ($1 == identify-chanserv) { set $varname_global(identify-chanserv,$network) $true }
  if ($1 == identify-nick) { return }
}
alias -l popup-identify-founder-list {
  if ($bool_using_proxy == $false) {  return $style(2) identify as &founder  }
  var %chan = $var($varname_global(identify-chanserv,$+(*,-,$$network)),1)
  var %chan = [ [ %chan ] ]
  if (%chan) { return identify as &founder }

}
alias www_run /run $scriptdir..\..\..\runall.bat $scriptdir..\..
alias true$false {
  return $true $+ $false
}
alias is_status_nick {
  ;check is active nick is either one of the two status nicks available.
  ;;

  if ($1) { var %nick = $1 }
  elseif ($nick != $null) { var %nick = $nick }
  if (~status != %nick) { return $false }
  return $true
}
menu menubar {
  $iif((!$var(%bde_glob_*history*,0)),$style(2)) erase history : unset %bde_glob_*history* | eecho you have erased your history.
  $iif(($os isin 7,10,11),&set client faster (High)) : eecho changed priority of all running $nopath($mircexe) and python3.exe (py.exe) apps to 'High' | run -hn wmic process where name=" $+ $nopath($mircexe) $+ " CALL setpriority 128 | run -hn wmic process where name="python.exe" CALL setpriority 128 | run -hn wmic process where name="py.exe" CALL setpriority 128 | run -hn wmic process where name="python3.exe" CALL setpriority 128
  -
  server commands
  .knock room $chan : /raw knock $$chan
  .help help : raw help help
  .help : raw help
  .-
  .info : raw info
  .time : raw time
  .-
  .users : raw users
  .long users : raw lusers
  .-
  .list channels : list
  .server links : raw links




}
on *:input:$chan: {
  if (*?> $chr(35) $+ ?* !iswm $1-) { return }
  tokenize 32 $strip($1-)
  if ($0 < 2) { return }
  var %num = $remove($2,$chr(35))
  if (!$isnum(%num)) { return }
  var %name = $remove($1,<,>,+,@,%,&,!)
  if (!%name) { return }
  msg %name xdcc send $chr(35) $+ %num
  halt
}
menu @script_info {
  close window : window -c $active
  -
  flood : /script_info -flood
  channel history : script_info -history
  identity : script_info -identity
  listen ip : script_info -listen
  listen port : script_info -port
}
alias bnc_msg {
  if (!$varname_glob(status-nick,none).value) { return }
  if ($bool_using_proxy != $true) { return }
  if ($strip($1) == $null) { return }
  if ($silence) { .msg $varname_glob(status-nick,none).value $1- }
  else { msg $varname_glob(status-nick,none).value $1- }
}
alias status_msg {
  bnc_msg $1-
}
alias errecho {
  if ($active == Status Window) { echo -a 4Error: $1- }
  else { echo -s 4Error: $1- }
}
