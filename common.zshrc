#!/bin/zsh
# vim: set filetype=zsh:

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

is_vim_bash_zsh() {
	local i=$(basename $1) m
	case $i in
	vi|vim|view) m=V;;
	bash) m=B;;
	zsh) m=Z;;
	sh) m='+';;
	esac
	[ -z "$m" ] && return 1
	__yunz_marks+="$m"
}

find_parent_process() {
	local pid cmd i=${3:-65535}

	pid=$PPID
	while [ $pid -ne 1 -a $i -gt 0 ]; do
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
		i=$((i-1))
	done
	return 1
}

unset __yunz_marks

if find_parent_process is_sshd; then
	__yunz_marks='*'
fi

if [ $SHLVL -gt 1 ]; then
	find_parent_process is_vim_bash_zsh 1 || true
fi

unset -f find_parent_process is_sshd is_vim_bash_zsh

function echocolor() {
	echo $'\e[1;38;5;'$1m"$2"$'\e[0m'
}

prompt_colors=(196 46 226 69 169 39 254 129 136 184 202)
precmd() {
	local i j n
	n=${#prompt_colors[*]}
	PS1=$'\n'
#	j="${__yunz_MARK_R:- }"
	j="${__yunz_marks}"

	i=$((RANDOM%n))
	if [ -n "${j/ /}" ]; then
		PS1+=$(echocolor ${prompt_colors[$i]} "$j")' '
#	else
#		PS1+='   '
	fi

	if [ -n "$ANDROID_SERIAL" ] && export | grep -s -q '\<ANDROID_SERIAL='; then
		i=$(((i+1)%n))
		PS1+=$(echocolor ${prompt_colors[$i]} "$ANDROID_SERIAL")' '
	fi

	i=$(((i+1)%n))
	PS1+=$(echocolor ${prompt_colors[$i]} $PROMPT_WD)
	PS1+=$'\n'"$PROMPT_ID"
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
export TERM=xterm-256color

yunz_make_easy
unset -f yunz_make_easy

