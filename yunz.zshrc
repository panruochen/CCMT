#!/bin/zsh
# vim: set filetype=zsh:
setopt KSH_ARRAYS

#============================================#
#   set up LS_COLORS
#============================================#
if [ -f ~/.dircolors ]; then
    eval $(dircolors ~/.dircolors)
fi

#============================================#
#   Load local settings
#============================================#
if [ -f ~/.localsettings.zshrc ]; then
	source ~/.localsettings.zhrc
fi

#============================================#
#   Aliases for easy usage
#============================================#
alias ls='\ls --color=auto'
alias cp='\cp -i'
alias rm='\rm -i'
alias mv='\mv -i'

is_sshd() {
	if echo "$1" | grep -q -s '^.*/sshd\>'; then
		[ -x "$1" ] && return 0
	fi
	return 1
}

find_parent_process_by_name() {
	local pid cmd

	pid=$PPID
	while [ $pid -ne 1 ]; do
		read -d $'\x00' cmd < /proc/$pid/cmdline
		if "$1" "${cmd}"; then
			return 0
		fi
		if [ -r /proc/$pid/ppid ]; then
			pid=$(cat /proc/$pid/ppid)
		else
			pid=$(ps -p $pid -o ppid=|tr -d '[:space:]') || {
				echo >&2 "Can not get parent process id"
				return 1
			}
		fi
	done
	return 1
}

if find_parent_process_by_name is_sshd; then
	ON_REMOTE='*'
else
	unset ON_REMOTE
fi
unset -f find_parent_process_by_name is_sshd

function echocolor() {
	echo $'\e[1;38;5;'$1m"$2"$'\e[0m'
}

prompt_colors=(196 46 226 69 169 39 254 129 136 184 202)
precmd() {
	local i j n
	n=${#prompt_colors[*]}
	PS1=$'\n'
	j="${ON_REMOTE:- }"
	if [ $SHLVL -gt 1 ]; then
		j+="^"
	else
		j+=' '
	fi
	i=$((RANDOM%n))
	if [ -z ${param/ /} ]; then
		PS1+=$(echocolor ${prompt_colors[$i]} "$j")' '
	else
		PS1+='   '
	fi

	if [ -n "$ANDROID_SERIAL" ] && export | grep -s -q '\<ANDROID_SERIAL='; then
		i=$(((i+1)%n))
		PS1+=$(echocolor ${prompt_colors[$i]} "$ANDROID_SERIAL")' '
	fi

	i=$(((i+1)%n))
	PS1+=$(echocolor ${prompt_colors[$i]} "%~")
	PS1+=$'\n%# '
	i=$((RANDOM%n))
	j=$((RANDOM%n))
	if [[ $i != $j ]]; then
		n=${prompt_colors[$i]}
		prompt_colors[$i]=${prompt_colors[$j]}
		prompt_colors[$j]=$n
	fi
#	PS1=%(!.#.$) # $ for non-root, # for root
}

yunz_make_easy() {
	local x y z
	[ -n "$MY_FRIENDLY_SERVERS" ] || return 0

	while read z
	do
		[ -n "$z" ] || continue
		read x y <<< "$z"
		read -d '@' z <<< "$y"
		eval "export RH_$(echo $x|tr '[a-z]' '[A-Z]')='$y:/home/$z'"
		eval "alias go-$x='ssh $y'"
	done <<< "$MY_FRIENDLY_SERVERS"
}

autoload -Uz chpwd_recent_dirs cdr add-zsh-hook
add-zsh-hook chpwd chpwd_recent_dirs
zstyle ':completion:*:*:cdr:*:*' menu selection

export TERM=xterm-256color

yunz_make_easy
unset -f yunz_make_easy

export PATH=$PATH:$(cd $(dirname ${(%):-%x}); pwd)
