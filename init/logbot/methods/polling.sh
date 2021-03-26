#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -i _to=1
declare -r _input=logs/logbot.stdin

startLogBotPolling() {
    test -z $BOT_TOKEN || _polling &
}

endLogBotPolling() {
    test -z $BOT_TOKEN || echo quit >> $_input
    wait
}

_polling() {
    local cmd func args
    _resetConnection
    log "LogBot Polling Started !"
    while true; do
        cmd="$(head -n 1 $_input 2> /dev/null && sed -i '1d' $_input)"
        test -z "$cmd" && _pollsleep && continue
        test $_to -gt 3 && let _to-=3
        case $cmd in
            quit)
                break;;
            deleteLastMessage|printMessages|deleteMessages)
                $cmd;;
            sendMessage*|replyLastMessage*|editLastMessage*)
                func=$(echo $cmd | cut -d' ' -f1)
                args=$(echo $cmd | cut -d' ' -f2-)
                $func "~$args";;
            *)
                log "unknown : < $cmd >"
                test -z $cmd && break;;
        esac
        sleep 1
    done
    log "LogBot Polling Ended !"
    _resetConnection
    exit 0
}

_resetConnection() {
    rm -f $_input
}

_pollsleep() {
    let _to+=1
    log "sleeping (${_to}s) (caused by \"LogBot.polling\")"
    sleep $_to
}