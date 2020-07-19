#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

sendMessage() {
    rawsendMessage $LOG_CHANNEL_ID "$1"
}

replyLastMessage() {
    getLastMessage reply "$1"
}

editLastMessage() {
    getLastMessage edit "$1"
}

deleteLastMessage() {
    getLastMessage delete
}

deleteMessages() {
    getMessageCount
    local count=$(($?))
    for ((i=0; i<$count; i++)); do
        deleteLastMessage
    done
}

printMessages() {
    for msg in $(getAllMessages); do
        printf "{%s: %s}\n" $msg "$($msg.print)"
    done
}

startLogBotPolling() {
    _polling &
}

_polling() {
    local cmd func args input=logs/logbot.stdin
    rm -f $input
    log "LogBot Polling Started !"
    while true; do
        cmd="$(head -n 1 $input 2> /dev/null && sed -i '1d' $input)"
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
    done
    log "Ended LogBot Polling !"
    exit 0
}

declare -i _to=1

_pollsleep() {
    let _to+=1
    log "sleeping ($_to) caused by (LogBot.polling)"
    sleep $_to
}
