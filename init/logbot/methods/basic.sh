#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

_delay=0.6

sendMessage() {
    test -z "$1" || rawsendMessage $LOG_CHANNEL_ID "$1"
    sleep $_delay
}

replyLastMessage() {
    test -z "$1" || getLastMessage reply "$1"
    sleep $_delay
}

editLastMessage() {
    test -z "$1" || getLastMessage edit "$1"
    sleep $_delay
}

deleteLastMessage() {
    getLastMessage delete
    sleep $_delay
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
