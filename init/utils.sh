#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -r pVer=$(sed -E 's/\w+ ([2-3])\.([0-9]+)\.([0-9]+)/\1.\2.\3/g' < <(python3 -V))

log() {
    local text="$*"
    test ${#text} -gt 0 && test ${text::1} != '~' && echo -e "[LOGS] >>> ${text#\~}"
}

quit() {
    local err="\t:: ERROR :: $1 -> Exiting ..."
    if (( getMessageCount )); then
        replyLastMessage "$err"
    else
        log "$err"
    fi
    exit 1
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
    echo ========================================================
}

printLogo() {
    printLine
    echo '
 _   _ ____  _____ ____   ____ _____  ____  _   _ _____ 
| | | / ___|| ____|  _ \ / ___| ____|/ __ \| | | |_   _|
| | | \___ \|  _| | |_) | |  _|  _| / / _` | | | | | |  
| |_| |___) | |___|  _ <| |_| | |__| | (_| | |_| | | |  
 \___/|____/|_____|_| \_\\____|_____\ \__,_|\___/  |_|  
                                     \____/
'
    printLine
}
