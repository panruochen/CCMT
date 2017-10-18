#!/bin/bash
# vim: set filetype=sh:

#============================================#
#   set up LS_COLORS
#============================================#
if [ -f ~/.dircolors ]; then
	eval $(dircolors ~/.dircolors)
fi

#============================================#
#   Aliases for easy usage
#============================================#
alias ls='\ls --color=auto'
alias cp='\cp -i'
alias rm='\rm -i'
alias mv='\mv -i'

ps1_fg_color() {
#	local fg_colors=(9 10 11 12 13 14 15 129 136 184 202)
	local fg_colors=(196 46 226 69 169 39 254 129 136 184 202)
	echo ${fg_colors[$((RANDOM%${#fg_colors[*]}))]}
}

export TERM=xterm-256color
export PS1='\e[1;38;5;$(ps1_fg_color)m\u@\h\e[0m \e[1;38;5;$(ps1_fg_color)m\w\e[0m\n\$'
