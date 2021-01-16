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
    WORKERS = int(os.environ.get("WORKERS")) or os.cpu_count() + 4
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)
    OWNER_ID = tuple(filter(lambda x: x, map(int, os.environ.get("OWNER_ID", "0").split())))
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
    AUTH_CHATS = (OWNER_ID[0], LOG_CHANNEL_ID) if OWNER_ID else (LOG_CHANNEL_ID,)
    DB_URI = os.environ.get("DATABASE_URL")
    LANG = os.environ.get("PREFERRED_LANGUAGE")
    DOWN_PATH = os.environ.get("DOWN_PATH")
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER")
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER")
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR")
    UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR")
    ALIVE_MEDIA = os.environ.get("ALIVE_MEDIA", None)
    CUSTOM_PACK_NAME = os.environ.get("CUSTOM_PACK_NAME")
    INSTA_ID = os.environ.get("INSTA_ID")
    INSTA_PASS = os.environ.get("INSTA_PASS")
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO")
    UPSTREAM_REMOTE = os.environ.get("UPSTREAM_REMOTE")
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
    LOAD_UNOFFICIAL_PLUGINS = os.environ.get(
        "LOAD_UNOFFICIAL_PLUGINS") == "true"
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
    DISABLED_ALL = False
    DISABLED_CHATS: Set[int] = set()
    ALLOWED_COMMANDS: Set[str] = set()
    ANTISPAM_SENTRY = False
    RUN_DYNO_SAVER = False
    HEROKU_APP = heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME] \
        if HEROKU_API_KEY and HEROKU_APP_NAME else None
    STATUS = None


def get_version() -> str:
    """ get userge version """
    ver = f"{versions.__major__}.{versions.__minor__}.{versions.__micro__}"
    if "/usergeteam/userge" in Config.UPSTREAM_REPO.lower():
        diff = list(_REPO.iter_commits(f'v{ver}..HEAD'))
        if diff:
            return f"{ver}-patch.{len(diff)}"
    else:
        diff = list(_REPO.iter_commits(
            f'{Config.UPSTREAM_REMOTE}/master..HEAD'))
        if diff:
            return f"{ver}-custom.{len(diff)}"
    return ver
