#!/bin/bash
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

_checkBashReq() {
    log "Checking Bash Commands ..."
    command -v jq &> /dev/null || quit "Required command : jq : could not be found !"
}

_checkPythonVersion() {
    log "Checking Python Version ..."
    test $(sed 's/\.//g' <<< $pVer) -lt 380 \
        && quit "You MUST have a python version of at least 3.8.0 !"
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
            && quit "Please remove the line mentioned in the first hashtag from the config.sh file"
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
        [WORKERS]=4
        [ANTISPAM_SENTRY]=false
        [PREFERRED_LANGUAGE]="en"
        [DOWN_PATH]="downloads"
        [UPSTREAM_REMOTE]="upstream"
        [UPSTREAM_REPO]="https://github.com/UsergeTeam/Userge"
        [LOAD_UNOFFICIAL_PLUGINS]=false
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
    DOWN_PATH=${DOWN_PATH%/}/
    [[ -n $HEROKU_API_KEY && -n $HEROKU_APP_NAME ]] \
        && declare -gx HEROKU_GIT_URL="https://api:$HEROKU_API_KEY@git.heroku.com/$HEROKU_APP_NAME.git"
    for var in ANTISPAM_SENTRY G_DRIVE_IS_TD LOAD_UNOFFICIAL_PLUGINS; do
        eval $var=$(tr "[:upper:]" "[:lower:]" <<< ${!var})
    done
    local nameAndUName=$(grep -oP "(?<=\/\/)(.+)(?=\@)" <<< $DATABASE_URL)
    DATABASE_URL=$(sed 's/$nameAndUName/$(printf "%q\n" $nameAndUName)/' <<< $DATABASE_URL)
}

_checkDatabase() {
    editLastMessage "Checking DATABASE_URL ..."
    local err=$(runPythonCode '
import pymongo
try:
    pymongo.MongoClient("'$DATABASE_URL'").list_database_names()
except Exception as e:
    print(e)')
    [[ $err ]] && quit "pymongo response > $err" || log "\tpymongo response > {status : 200}"
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

_checkGit() {
    editLastMessage "Checking GIT ..."
    if test ! -d .git; then
        if test -n $HEROKU_GIT_URL; then
            replyLastMessage "\tClonning Heroku Git ..."
            gitClone $HEROKU_GIT_URL tmp_git || quit "Invalid HEROKU_API_KEY or HEROKU_APP_NAME var !"
            mv tmp_git/.git .
            rm -rf tmp_git
        else
            replyLastMessage "\tInitializing Empty Git ..."
            gitInit
        fi
        deleteLastMessage
    fi
}

_checkUpstreamRepo() {
    editLastMessage "Checking UPSTREAM_REPO ..."
    grep -q $UPSTREAM_REMOTE < <(git remote) || addUpstream
    replyLastMessage "\tFetching Data From UPSTREAM_REPO ..."
    fetchUpstream || updateUpstream && fetchUpstream || quit "Invalid UPSTREAM_REPO var !"
    deleteLastMessage
}

_checkUnoffPlugins() {
    editLastMessage "Checking UnOfficial Plugins ..."
    if test $LOAD_UNOFFICIAL_PLUGINS = true; then
        editLastMessage "\tLoading UnOfficial Plugins ..."
        replyLastMessage "\t\tClonning ..."
        gitClone --depth=1 https://github.com/UsergeTeam/Userge-Plugins.git
        editLastMessage "\t\tUpgrading PIP ..."
        upgradePip
        editLastMessage "\t\tInstalling Requirements ..."
        installReq Userge-Plugins
        editLastMessage "\t\tCleaning ..."
        rm -rf userge/plugins/unofficial/
        mv Userge-Plugins/plugins/ userge/plugins/unofficial/
        cp -r Userge-Plugins/resources/* resources/
        rm -rf Userge-Plugins/
        deleteLastMessage
        editLastMessage "\tUnOfficial Plugins Loaded Successfully !"
    else
        editLastMessage "\tUnOfficial Plugins Disabled !"
    fi
    sleep 1
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
    _checkGit
    _checkUpstreamRepo
    _checkUnoffPlugins
}
