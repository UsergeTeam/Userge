#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

declare -i bgProc

_addHandler() {
    trap killProc HUP TERM INT
}

_removeHandler() {
    trap - HUP TERM INT
}

setProc() {
    bgProc=$1
}

_waitProc() {
    test $bgProc && wait $bgProc
}

waitProc() {
    _waitProc
    _removeHandler
    _waitProc
}

killProc() {
    test $bgProc && kill -TERM $bgProc &> /dev/null
}

reInitProc() {
    killProc
    waitProc
    _addHandler
}
