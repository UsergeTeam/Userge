#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -r pVer=$(sed -E 's/\w+ 3\.8\.([0-9]+)/3.8.\1/g' < <(python3.8 -V 2> /dev/null))

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

fetchBranches() {
    local r_bs l_bs
    r_bs=$(grep -oP '(?<=refs/heads/)\w+' < <(git ls-remote --heads $UPSTREAM_REMOTE))
    l_bs=$(grep -oP '\w+' < <(git branch))
    for r_b in $r_bs; do
        [[ $l_bs =~ $r_b ]] || git branch $r_b $UPSTREAM_REMOTE/$r_b &> /dev/null
    done
}

upgradePip() {
    pip3 install -U pip &> /dev/null
}

installReq() {
    pip3 install -r $1/requirements.txt &> /dev/null
}

printLine() {
    echo '->- ->- ->- ->- ->- ->- ->- --- -<- -<- -<- -<- -<- -<- -<-'
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
