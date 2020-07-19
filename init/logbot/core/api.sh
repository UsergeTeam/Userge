#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -r _api_url="https://api.telegram.org/bot"
declare -i _mid=0
declare -a _allMessages=()

_getResponse() {
    if [[ -n $BOT_TOKEN && -n $LOG_CHANNEL_ID ]]; then
        local reqType=$1 parse=false; shift
        test ${reqType::4} = "send" && parse=true
        local params=$(sed 's/ /\&/g' <<< $*)
        test -n $params && params="?$params"
        local rawUpdate=$(curl -s ${_api_url}${BOT_TOKEN}/${reqType}${params})
        local ok=$(echo $rawUpdate | jq .ok)
        if test $ok = true; then
            if test $parse = true; then
                local msg="msg$_mid"
                Message $msg
                $msg.parse $_mid "$rawUpdate"
                _allMessages[$_mid]=$msg
                let _mid+=1
            fi
        else
            quit "invalid request ! caused by (core.Api.$FUNCNAME)\n$rawUpdate"
        fi
    fi
}

_urlEncode() {
    echo $(echo "${1#\~}" | sed -E 's/(\\t)|(\\n)/ /g' |
        curl -Gso /dev/null -w %{url_effective} --data-urlencode @- "" | cut -c 3-)
}

getMessageCount() {
    return ${#_allMessages[@]}
}

getAllMessages() {
    echo ${_allMessages[@]}
}

getLastMessage() {
    if test ${#_allMessages[@]} -gt 0; then
        ${_allMessages[-1]}.$1 "$2"
    elif [[ -n $BOT_TOKEN && -n $LOG_CHANNEL_ID ]]; then
        log "first sendMessage ! caused by (core.Api.$FUNCNAME)\n"$2""
    else
        log "$2"
    fi
}

getUpdates() {
    local params=($*)
    _getResponse $FUNCNAME ${params[*]}
}

rawsendMessage() {
    local params=(
        chat_id=$1
        text=$(_urlEncode "$2")
    )
    test -n $3 && params+=(reply_to_message_id=$3)
    log "$2"
    _getResponse ${FUNCNAME#raw} ${params[*]}
}

raweditMessageText() {
    local params=(
        chat_id=$1
        message_id=$2
        text=$(_urlEncode "$3")
    )
    log "$3"
    _getResponse ${FUNCNAME#raw} ${params[*]}
}

rawdeleteMessage() {
    local params=(
        chat_id=$1
        message_id=$2
    )
    unset _allMessages[$3]
    _getResponse ${FUNCNAME#raw} ${params[*]}
}
