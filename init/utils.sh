#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -r pVer=$(sed -E 's/\w+ ([2-3])\.([0-9]+)\.([0-9]+)/\1.\2.\3/g' < <(python3.8 -V))

log() {
    local text="$*"
    test ${#text} -gt 0 && test ${text::1} != '~' \
        && echo -e "[$(date +'%d-%b-%y %H:%M:%S') - INFO] - init - ${text#\~}"
}

quit() {
    local err="\t:: ERROR :: $1\nExiting With SIGTERM (143) ..."
    if (( getMessageCount )); then
        replyLastMessage "$err"
    else
        log "$err"
    fi
    exit 143
}

runPythonCode() {
    python${pVer%.*} -c "$1"
}

runPythonModule() {
    python${pVer%.*} -m "$@"
}

gitInit() {
    git init &> /dev/null
    git commit --allow-empty -m "empty commit" &> /dev/null
}

gitClone() {
    git clone "$@" &> /dev/null
}

remoteIsExist() {
    grep -q $1 < <(git remote)
}

addHeroku() {
    git remote add heroku $HEROKU_GIT_URL
}

addUpstream() {
    git remote add $UPSTREAM_REMOTE ${UPSTREAM_REPO%.git}.git
}

updateUpstream() {
    git remote rm $UPSTREAM_REMOTE && addUpstream
}

fetchUpstream() {
    git fetch $UPSTREAM_REMOTE &> /dev/null
}

upgradePip() {
    pip3 install -U pip &> /dev/null
}

installReq() {
    pip3 install -r $1/requirements.txt &> /dev/null
}

printLine() {
    echo '-<- -<- -<- -<- -<- -<- -<- -<- -<- -<- -<- -<- -<- -<- -<-'
}

printLogo() {
    printLine
    echo '
     ________            __  __               ______   
    /_  __/ /_  ___     / / / /_______  _____/ ____/__ 
     / / / __ \/ _ \   / / / / ___/ _ \/ ___/ / __/ _ \
    / / / / / /  __/  / /_/ (__  )  __/ /  / /_/ /  __/
   /_/ /_/ /_/\___/   \____/____/\___/_/   \____/\___/ 
                                                     
'
    printLine
}
