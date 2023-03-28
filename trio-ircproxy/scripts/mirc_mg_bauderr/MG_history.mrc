on *:start:exp_topics
on *:exit:exp_topics
on *:load:exp_topics
on *:connect:exp_topics

alias exp_topics {
  var %check = $varname_global(topic_history_*,*)
  var %i = 0
  :loop
  inc %i
  %check2 = $var($eval(%check,1),%i)
  if (%check2 == $null) { return }
  if ($calc($ctime - $gettok(%check2,-1,35)) > $calc(60 * 60 * 24 * 14)) { unset $eval(%check2,1) | dec %i }
  goto loop
}
on *:topic:#: {
  var %topic = $strip($1-)
  if (%topic == $null) { return }
  topic_history_add $chan $1-
}
raw 332:*: {
  if ($strip($3) == $null) { return }
  topic_history_add $2 $3-

}
alias topic_history_remove {
  if (!$1) { return }
  unset $varname_global(topic_history_ $+ $1,*)
}
alias topic_history_add {
  var %chan = $1
  if (!$strip(%chan)) || (!$strip($2-)) { return }
  var %i = 0
  var %check = $varname_global(topic_history_ $+ %chan,*)
  var %varname
  :loop
  if (%i > 15) { return }
  inc %i
  %varname = $var($eval(%check,1),%i)
  if (!%varname) { goto end }
  if ([ [ %varname ] ] === $2-) { return }
  goto loop
  :end
  set $varname_global(topic_history_ $+ %chan,$ctime) $2-

}
alias topic_history_popup {
  if ($1 == begin) { return }
  if ($1 == end) { return }
  if ($1 > 16) { halt }
  var %chan = $chan
  if (!%chan) && ($1 == 1) { return $style(2) - not a channel - : return }
  if (!%chan) || (!$1) { return }
  if ($1 == 16) {
    unset $var($varname_global(topic_history_ $+ %chan,*),1)
  }
  var %check = $varname_global(topic_history_ $+ %chan,*)
  ; eval is set to 1 because it gets evaluated when displayed
  var %topic = $var($eval(%check,1),$1)
  if (%topic == $null) { return }
  var %top-pop = $strip($eval(%topic,2))
  if ($len(%top-pop) > 60) { %top-pop = $left(%top-pop, 58) ... }
  %top-pop = $replace(%top-pop,$,$)
  return $replace(%top-pop,:,!) : /editbox /topic %chan $eval(%topic,1)
}
