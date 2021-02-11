#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -r _api_url="https://api.telegram.org/bot"
declare -i _mid=0 _isChecked=0
declare -a _allMessages=()

_getResponse() {
    if [[ -n $BOT_TOKEN && -n $LOG_CHANNEL_ID ]]; then
        local reqType=${1#api.} parse=false; shift
        test ${reqType::4} = "send" && parse=true
        local params=$(sed 's/ /\&/g' <<< $*)
        test -n $params && params="?$params"
        local rawUpdate=$(curl -s ${_api_url}${BOT_TOKEN}/${reqType}${params})
        local ok=$(echo $rawUpdate | jq .ok)
        test -z $ok && return 1
        if test $ok = true; then
            if test $_isChecked -eq 0; then
                local chatType=$(echo $rawUpdate | jq .result.chat.type)
                [[ $chatType == \"supergroup\" || $chatType == \"channel\" ]] || \
                    quit "invalid log chat type ! [$chatType]"
                local chatUsername=$(echo $rawUpdate | jq .result.chat.username)
                test $chatUsername != null && quit "log chat should be private !"
                _isChecked=1
            fi
            if test $parse = true; then
                local msg="msg$_mid"
                Message $msg
                $msg.parse $_mid "$rawUpdate"
                _allMessages[$_mid]=$msg
                let _mid+=1
            fi
        else
            local errcode=$(echo $rawUpdate | jq .error_code)
            local desc=$(echo $rawUpdate | jq .description)
            quit "invalid request ! (caused by core.api.$FUNCNAME)
\terror_code : [$errcode]
\tdescription : $desc"
        fi
        sleep 0.6
    fi
}
