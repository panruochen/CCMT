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
alias grep='\grep --color=auto'
alias cp='\cp -i'
alias rm='\rm -i'
alias mv='\mv -i'

is_sshd() {
	if echo "$1" | grep -q -s '^.*/sshd\>'; then
		[ -x "$1" ] && return 0
	fi
	return 1
}

get_vim_mark() {
	local i=$(basename -- "$1")
	case "$i" in
	vi|vim|view) __yunz_marks+=V; return 0;;
	esac
	return 1
}

get_shell_mark() {
	local i=$(basename -- "$1")
	case "$i" in
	bash|-bash) m=B;;
	zsh|-zsh) m=Z;;
	sh|-sh)
		# https://stackoverflow.com/questions/3327013/how-to-determine-the-current-shell-im-working-on
		if [ -n "$BASH" ]; then m='B'
		elif [ -n "$ZSH_NAME" ]; then m='Z'
		else m='X'
		fi
		;;
	esac
	__yunz_marks+="$m"
}

find_parent_process() {
	local pid cmd i=0

#	pid=$PPID
	pid=$$
	while [ $pid -ne 1 -a $i -lt 65535 ]; do
		read -d $'\x00' cmd < /proc/$pid/cmdline
		if [ -n "$2" ]; then
			eval "$2+=(\"$cmd\")"
		fi
		if [ -r /proc/$pid/ppid ]; then
			pid=$(cat /proc/$pid/ppid)
		else
			pid=$(ps -p $pid -o ppid=|tr -d '[:space:]') || {
				echo >&2 "Can not get parent process id"
				return 1
			}
		fi
		if [ $((i+=1)) -eq 1 ]; then
			continue
		fi
		if "$1" "${cmd}"; then
			return 0
		fi
	done
	return 1
}

unset __yunz_marks
pps=()

if find_parent_process is_sshd pps; then
	__yunz_marks='*'
else
	__yunz_marks='-'
fi

if [ $SHLVL -gt 1 ]; then
	get_vim_mark "${pps[1]}" || get_shell_mark "${pps[1]}"
else
	__yunz_marks+='-'
fi

get_shell_mark "${pps[0]}"

unset pps
unset -f find_parent_process is_sshd get_vim_mark get_shell_mark

function echocolor() {
	echo $'\e[1;38;5;'$1m"$2"$'\e[0m'
}

function stripcolor() {
	local f o

	if [ "$1" = -i ]; then
		o="-i"
		shift 1
	fi
	f="${1:-/dev/stdin}"
# remove color sequence
	sed $o s/$'\x1b''[[][0-9;]\+m'//g $f
}

prompt_colors=(196 46 226 69 169 39 254 129 136 184 202)
precmd() {
	local i j n
	n=${#prompt_colors[*]}
	PS1=$'\n'
#	j="${__yunz_MARK_R:- }"
	[ -n "$YUNZ_HOSTNAME" ] && j+="$YUNZ_HOSTNAME "
	j+="${__yunz_marks}"

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
	PS1+=$'\n'"$PROMPT_ID "
	i=$((RANDOM%n))
	j=$((RANDOM%n))
	if [[ $i != $j ]]; then
		n=${prompt_colors[$i]}
		prompt_colors[$i]=${prompt_colors[$j]}
		prompt_colors[$j]=$n
	fi
#	PS1=%(!.#.$) # $ for non-root, # for root
}

changetitle() {
    local cmd
    cmd="'\\e]0;$1\\a'"
    eval echo -ne "$cmd"
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

