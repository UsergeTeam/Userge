# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Config', 'get_version']

import os
from typing import Set

import heroku3
from git import Repo
from pyrogram import filters

from userge import logging, logbot
from . import versions

_REPO = Repo()
_LOG = logging.getLogger(__name__)
logbot.reply_last_msg("Setting Configs ...")


class Config:
    """ Configs to setup Userge """
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    WORKERS = min(32, int(os.environ.get("WORKERS")) or os.cpu_count() + 4)
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
    DB_URI = os.environ.get("DATABASE_URL")
    LANG = os.environ.get("PREFERRED_LANGUAGE")
    DOWN_PATH = os.environ.get("DOWN_PATH")
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER")
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER")
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR")
    UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR")
    CUSTOM_PACK_NAME = os.environ.get("CUSTOM_PACK_NAME")
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE")
    SCREENSHOT_API = os.environ.get("SCREENSHOT_API", None)
    SPAM_WATCH_API = os.environ.get("SPAM_WATCH_API", None)
    CURRENCY_API = os.environ.get("CURRENCY_API", None)
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", None)
    OPEN_WEATHER_MAP = os.environ.get("OPEN_WEATHER_MAP", None)
    REMOVE_BG_API_KEY = os.environ.get("REMOVE_BG_API_KEY", None)
    WEATHER_DEFCITY = os.environ.get("WEATHER_DEFCITY", None)
    TZ_NUMBER = os.environ.get("TZ_NUMBER", 1)
    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID", None)
    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET", None)
    G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID", None)
    G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK", None)
    GOOGLE_CHROME_DRIVER = os.environ.get("GOOGLE_CHROME_DRIVER", None)
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN", None)
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    G_DRIVE_IS_TD = os.environ.get("G_DRIVE_IS_TD") == "true"
    LOAD_UNOFFICIAL_PLUGINS = os.environ.get("LOAD_UNOFFICIAL_PLUGINS") == "true"
    THUMB_PATH = DOWN_PATH + "thumb_image.jpg"
    TMP_PATH = "userge/plugins/temp/"
    MAX_MESSAGE_LENGTH = 4096
    MSG_DELETE_TIMEOUT = 120
    WELCOME_DELETE_TIMEOUT = 120
    EDIT_SLEEP_TIMEOUT = 10
    AUTOPIC_TIMEOUT = 300
    ALLOWED_CHATS = filters.chat([])
    ALLOW_ALL_PMS = True
    USE_USER_FOR_CLIENT_CHECKS = False
    SUDO_ENABLED = False
    SUDO_USERS: Set[int] = set()
    ALLOWED_COMMANDS: Set[str] = set()
    ANTISPAM_SENTRY = False
    RUN_DYNO_SAVER = False
    HEROKU_APP = None
    STATUS = None


if Config.HEROKU_API_KEY:
    logbot.reply_last_msg("Checking Heroku App...", _LOG.info)
    for heroku_app in heroku3.from_key(Config.HEROKU_API_KEY).apps():
        if (heroku_app and Config.HEROKU_APP_NAME
                and heroku_app.name == Config.HEROKU_APP_NAME):
            _LOG.info("Heroku App : %s Found...", heroku_app.name)
            Config.HEROKU_APP = heroku_app
            break
    logbot.del_last_msg()


try:
    for ref in _REPO.remote(Config.UPSTREAM_REMOTE).refs:
        branch = str(ref).split('/')[-1]
        if branch not in _REPO.branches:
            _REPO.create_head(branch, ref)
except ValueError as v_e:
    _LOG.error(v_e)


def get_version() -> str:
    """ get userge version """
    ver = f"{versions.__major__}.{versions.__minor__}.{versions.__micro__}"
    if "/usergeteam/userge" in Config.UPSTREAM_REPO.lower():
        diff = list(_REPO.iter_commits(f'v{ver}..HEAD'))
        if diff:
            return f"{ver}-patch.{len(diff)}"
    else:
        diff = list(_REPO.iter_commits(f'{Config.UPSTREAM_REMOTE}/master..HEAD'))
        if diff:
            return f"{ver}-custom.{len(diff)}"
    return ver
