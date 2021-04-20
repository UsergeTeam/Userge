#!/bin/bash
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

_checkBashReq() {
    log "Checking Bash Commands ..."
    command -v jq &> /dev/null || quit "Required command : jq : could not be found !"
}

_checkPythonVersion() {
    log "Checking Python Version ..."
    getPythonVersion
    ( test -z $pVer || test $(sed 's/\.//g' <<< $pVer) -lt 3${minPVer}0 ) \
        && quit "You MUST have a python version of at least 3.$minPVer.0 !"
    log "\tFound PYTHON - v$pVer ..."
}

_checkConfigFile() {
    log "Checking Config File ..."
    configPath="config.env"
    if test -f $configPath; then
        log "\tConfig file found : $configPath, Exporting ..."
        set -a
        . $configPath
        set +a
        test ${_____REMOVE_____THIS_____LINE_____:-fasle} = true \
            && quit "Please remove the line mentioned in the first hashtag from the config.env file"
    fi
}

_checkRequiredVars() {
    log "Checking Required ENV Vars ..."
    for var in API_ID API_HASH LOG_CHANNEL_ID DATABASE_URL; do
        test -z ${!var} && quit "Required $var var !"
    done
    [[ -z $HU_STRING_SESSION && -z $BOT_TOKEN ]] && quit "Required HU_STRING_SESSION or BOT_TOKEN var !"
    [[ -n $BOT_TOKEN && -z $OWNER_ID ]] && quit "Required OWNER_ID var !"
    test -z $BOT_TOKEN && log "\t[HINT] >>> BOT_TOKEN not found ! (Disabling Advanced Loggings)"
}

_checkDefaultVars() {
    replyLastMessage "Checking Default ENV Vars ..."
    declare -rA def_vals=(
        [WORKERS]=0
        [PREFERRED_LANGUAGE]="en"
        [DOWN_PATH]="downloads"
        [UPSTREAM_REMOTE]="upstream"
        [UPSTREAM_REPO]="https://github.com/UsergeTeam/Userge"
        [LOAD_UNOFFICIAL_PLUGINS]=false
        [CUSTOM_PLUGINS_REPO]=""
        [G_DRIVE_IS_TD]=true
        [CMD_TRIGGER]="."
        [SUDO_TRIGGER]="!"
        [FINISHED_PROGRESS_STR]="█"
        [UNFINISHED_PROGRESS_STR]="░"
    )
    for key in ${!def_vals[@]}; do
        set -a
        test -z ${!key} && eval $key=${def_vals[$key]}
        set +a
    done
    if test $WORKERS -le 0; then
        WORKERS=$(($(nproc)+4))
    elif test $WORKERS -gt 32; then
        WORKERS=32
    fi
    export MOTOR_MAX_WORKERS=$WORKERS
    export HEROKU_ENV=$(test $DYNO && echo 1 || echo 0)
    DOWN_PATH=${DOWN_PATH%/}/
    if [[ $HEROKU_ENV == 1 && -n $HEROKU_API_KEY && -n $HEROKU_APP_NAME ]]; then
        local herokuErr=$(runPythonCode '
import heroku3
try:
    if "'$HEROKU_APP_NAME'" not in heroku3.from_key("'$HEROKU_API_KEY'").apps():
        raise Exception("Invalid HEROKU_APP_NAME \"'$HEROKU_APP_NAME'\"")
except Exception as e:
    print(e)')
        [[ $herokuErr ]] && quit "heroku response > $herokuErr"
    fi
    for var in G_DRIVE_IS_TD LOAD_UNOFFICIAL_PLUGINS; do
        eval $var=$(tr "[:upper:]" "[:lower:]" <<< ${!var})
    done
    local uNameAndPass=$(grep -oP "(?<=\/\/)(.+)(?=\@cluster)" <<< $DATABASE_URL)
    local parsedUNameAndPass=$(runPythonCode '
from urllib.parse import quote_plus
print(quote_plus("'$uNameAndPass'"))')
    DATABASE_URL=$(sed 's/$uNameAndPass/$parsedUNameAndPass/' <<< $DATABASE_URL)
}

_checkDatabase() {
    editLastMessage "Checking DATABASE_URL ..."
    local mongoErr=$(runPythonCode '
import pymongo
try:
    pymongo.MongoClient("'$DATABASE_URL'").list_database_names()
except Exception as e:
    print(e)')
    [[ $mongoErr ]] && quit "pymongo response > $mongoErr" || log "\tpymongo response > {status : 200}"
}

_checkTriggers() {
    editLastMessage "Checking TRIGGERS ..."
    test $CMD_TRIGGER = $SUDO_TRIGGER \
        && quit "Invalid SUDO_TRIGGER!, You can't use $CMD_TRIGGER as SUDO_TRIGGER"
}

_checkPaths() {
    editLastMessage "Checking Paths ..."
    for path in $DOWN_PATH logs bin; do
        test ! -d $path && {
            log "\tCreating Path : ${path%/} ..."
            mkdir -p $path
        }
    done
}

_checkBins() {
    editLastMessage "Checking BINS ..."
    declare -rA bins=(
        [bin/megadown]="https://raw.githubusercontent.com/yshalsager/megadown/master/megadown"
        [bin/cmrudl]="https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py"
    )
    for bin in ${!bins[@]}; do
        test ! -f $bin && {
            log "\tDownloading $bin ..."
            curl -so $bin ${bins[$bin]}
        }
    done
}

_checkUpstreamRepo() {
    remoteIsExist $UPSTREAM_REMOTE || addUpstream
    editLastMessage "Fetching Data From UPSTREAM_REPO ..."
    fetchUpstream || updateUpstream && fetchUpstream || quit "Invalid UPSTREAM_REPO var !"
    fetchBranches
    updateBuffer
}

_setupPlugins() {
    local link path tmp
    if test $(grep -P '^'$2'$' <<< $3); then
        editLastMessage "Cloning $1 Plugins ..."
        link=$(test $4 && echo $4 || echo $3)
        tmp=Temp-Plugins
        gitClone --depth=1 $link $tmp
        replyLastMessage "\tInstalling Requirements ..."
        upgradePip
        installReq $tmp
        path=$(tr "[:upper:]" "[:lower:]" <<< $1)
        rm -rf userge/plugins/$path/
        mv $tmp/plugins/ userge/plugins/$path/
        cp -r $tmp/resources/. resources/
        rm -rf $tmp/
        deleteLastMessage
    else
        editLastMessage "$1 Plugins Disabled !"
    fi
}

_checkUnoffPlugins() {
    _setupPlugins UnOfficial true $LOAD_UNOFFICIAL_PLUGINS https://github.com/UsergeTeam/Userge-Plugins.git
}

_checkCustomPlugins() {
    _setupPlugins Custom "https://([0-9a-f]{40}@)?github.com/.+/.+" $CUSTOM_PLUGINS_REPO
}

_flushMessages() {
    deleteLastMessage
}

assertPrerequisites() {
    _checkBashReq
    _checkPythonVersion
    _checkConfigFile
    _checkRequiredVars
}

assertEnvironment() {
    _checkDefaultVars
    _checkDatabase
    _checkTriggers
    _checkPaths
    _checkBins
    _checkUpstreamRepo
    _checkUnoffPlugins
    _checkCustomPlugins
    _flushMessages
}
