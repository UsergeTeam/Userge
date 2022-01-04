#!/bin/bash
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

. init/logbot/logbot.sh
. init/proc.sh
. init/utils.sh
. init/checks.sh

trap 'handleSig SIGHUP' HUP
trap 'handleSig SIGTERM' TERM
trap 'handleSig SIGINT' INT
trap '' USR1

handleSig() {
    log "Exiting With $1 ..."
    killProc
}

initUserge() {
    printLogo
    assertPrerequisites
    sendMessage "Initializing Userge ..."
    assertEnvironment
    editLastMessage "Starting Userge ..."
    printLine
}

startUserge() {
    startLogBotPolling
    runPythonModule userge "$@"
}

stopUserge() {
    sendMessage "Exiting Userge ..."
    endLogBotPolling
}

runUserge() {
    initUserge
    startUserge "$@"
    local code=$?
    stopUserge
    return $code
}
