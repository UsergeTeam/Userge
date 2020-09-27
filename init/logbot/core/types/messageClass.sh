#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -a _Message_properties=()

id=0
chat_id=1
message_id=2
text=3

_Message.property() {
    test "$2" = "=" && _Message_properties[$1]="$3" || echo "${_Message_properties[$1]}"
}

_Message.id() {
    test "$1" = "=" && _Message.property id = $2 || _Message.property id
}

_Message.chat_id() {
    test "$1" = "=" && _Message.property chat_id = $2 || _Message.property chat_id
}

_Message.message_id() {
    test "$1" = "=" && _Message.property message_id = $2 || _Message.property message_id
}

_Message.text() {
    test "$1" = "=" && _Message.property text = "$2" || _Message.property text
}

_Message.parse() {
    _Message.id = $1
    _Message.chat_id = $(echo $2 | jq .result.chat.id)
    _Message.message_id = $(echo $2 | jq .result.message_id)
    _Message.text = "$(echo $2 | jq -r .result.text)"
}

_Message.print() {
    printf "{id: %s, chat_id: %s, message_id: %s, text: %s}\n" \
$(_Message.id) $(_Message.chat_id) $(_Message.message_id) "$(_Message.text)"
}

_Message.edit() {
    api.editMessageText $(_Message.chat_id) $(_Message.message_id) "$1"
    _Message.text = "$1"
}

_Message.reply() {
    api.sendMessage $(_Message.chat_id) "$1" $(_Message.message_id)
}

_Message.delete() {
    api.deleteMessage $(_Message.chat_id) $(_Message.message_id) $(_Message.id)
}
