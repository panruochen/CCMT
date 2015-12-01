#!/bin/sh
#==============================================================#
# Correct user name and email address before pushing to remote #
#==============================================================#
git filter-branch --env-filter '
CORRECT_NAME="Pan Ruochen"
CORRECT_EMAIL="ijkxyz@msn.com"
if [ "$GIT_COMMITTER_EMAIL" = "$CORRECT_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" != "$CORRECT_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags

exit 0
