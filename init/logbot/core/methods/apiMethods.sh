#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

. init/logbot/core/utils.sh

api.getUpdates() {
    local params=($*)
    _getResponse $FUNCNAME ${params[*]}
}

api.sendMessage() {
    local params=(
        chat_id=$1
        text=$(urlEncode "$2")
        parse_mode=HTML
    )
    test -n $3 && params+=(reply_to_message_id=$3)
    log "$2"
    _getResponse $FUNCNAME ${params[*]}
}

api.editMessageText() {
    local params=(
        chat_id=$1
        message_id=$2
        text=$(urlEncode "$3")
        parse_mode=HTML
    )
    log "$3"
    _getResponse $FUNCNAME ${params[*]}
}

api.deleteMessage() {
    local params=(
        chat_id=$1
        message_id=$2
    )
    unset _allMessages[$3]
    _getResponse $FUNCNAME ${params[*]}
}
