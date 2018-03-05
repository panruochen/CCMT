#!/bin/bash
# vim: set filetype=sh:

#============================================#
#   set up LS_COLORS
#============================================#
if [ -f ~/.dircolors ]; then
    eval $(dircolors ~/.dircolors)
fi

#============================================#
#   Load local settings
#============================================#
if [ -f ~/.localsettings.bashrc ]; then
	source ~/.localsettings.bashrc
fi

#============================================#
#   Aliases for easy usage
#============================================#
alias ls='\ls --color=auto'
alias cp='\cp -i'
alias rm='\rm -i'
alias mv='\mv -i'

echocolor() {
	echo -e "\\e[1;38;5;${2:-255}m$1\\e[0m"
}

yunzBashEnv_SetColor() {
    colors=(196 46 226 69 169 39 254 129 136 184 202)
    echo ${colors[$((RANDOM%${#colors[*]}))]}
}

yunzBashEnv_HOSTNAME=(${LOCALHOST:-$HOSTNAME}
	$(ifconfig | grep -o 'inet addr:\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}' | \
	sed 's/^inet addr://' | head -n1))

PROMPT_COMMAND='yunzBashEnv_GlobalCounter=$((yunzBashEnv_GlobalCounter+1));'
export TERM=xterm-256color
PS1=$(read -d $'\x00' -r a < /proc/$PPID/cmdline; a="${a##*/}";
  case "$a" in (vi|vim|view|vimdiff) echo "($a) ";; esac)
#export PS1+='\e[1;38;5;$(yunzBashEnv_SetColor)m\u@\h\e[0m \e[1;38;5;$(yunzBashEnv_SetColor)m\w\e[0m\n\$'
PS1+='\e[1;38;5;$(yunzBashEnv_SetColor)m'
PS1+='${yunzBashEnv_HOSTNAME[$((yunzBashEnv_GlobalCounter%2))]}'
PS1+='>\e[0m \e[1;38;5;$(yunzBashEnv_SetColor)m\w\e[0m\n\$'
export PS1

export PATH=$PATH:$(dirname ${BASH_SOURCE[0]})
shopt -s checkjobs
