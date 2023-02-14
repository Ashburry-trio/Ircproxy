
on *:signal:baud_unload: {
  mg_set_app
}
on *:load: {
  baud_load_all
}
on *:start: {
  mg_set_app
}
on *:unload: {
  mg_set_app
}
alias baud_load_all {
  mg_set_app
  signal -n baud_unload
  load -rs $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_history.mrc)
  load -rs $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_menus.mrc)
  load -rs $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_no-category.mrc)
  load -ps $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_popups.ini)
  load -pc $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_popups.ini)
  load -pq $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_popups.ini)
  load -pn $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_popups.ini)
  load -pm $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\MG_popups.ini)
  var %fn = MG_Users-for- $+ %mg_app $+ .mrc
  /load -ru $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\ $+ %fn)
  var %fn = MG_Vars-for- $+ %mg_app $+ .mrc
  /load -rv $qt($scriptdirtrio-ircproxy\scripts\mirc_mg_bauderr\ $+ %fn)


}
alias -l mg_set_app {
  if (adiirc isin $mircexe) { set %mg_app Adiirc }
  if (mirc isin $mircexe) { set %mg_app mIRC }
  if ($version == 4.2) { set %mg_app Adiirc }
  if ($version > 7.0) { set %mg_app mIRC }

}
