#!/bin/zsh
# vim: set filetype=zsh:

__yunzrc_dir=$(cd $(dirname ${(%):-%x}); pwd)
export PATH=$PATH:$__yunzrc_dir

PROMPT_WD='%~'
PROMPT_ID='%#'

setopt KSH_ARRAYS
source $__yunzrc_dir/common.zshrc
unset __yunzrc_dir

autoload -Uz chpwd_recent_dirs cdr add-zsh-hook
add-zsh-hook chpwd chpwd_recent_dirs
zstyle ':completion:*:*:cdr:*:*' menu selection

