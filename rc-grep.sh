#!/bin/bash
#========================================================
#
#  A helper script to combining find+xargs for searching
#
#========================================================
#set -e -o pipefail

eval ARGV=($(getopt -l '' -o 'e:li' -- "$@")) || exit 1
grep_options=()
find_options=()
for((i=0;i<${#ARGV[@]};i++)) {
    o="${ARGV[$i]}"
    case $o in
    -e)
        i=$((i+1));
		a="${ARGV[$i]}"
		grep_options+=("-e" "$a")
		;;
	-i)
		grep_options+=("-i")
		;;
	-l)
		grep_options+=("-l")
		;;
	--)
        i=$((i+1));
		break;;
    esac
}

for((;i<${#ARGV[@]};i++)) {
	if [ -n "$find_options" ]; then
		find_options+=("-o")
	fi
	a="${ARGV[$i]}"
	find_options+=("-name" "$a")
}

set +e
find \( -type f -a \( "${find_options[@]}" \) \) -print0| xargs -0 grep "${grep_options[@]}"


