# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Config']

import os
import sys
import shutil
from typing import Set

import heroku3
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError
from pySmartDL import SmartDL
from dotenv import load_dotenv
from pyrogram import Filters

from userge import logging
from . import versions

_LOG = logging.getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    _LOG.error("You MUST have a python version of at least 3.7 !")
    sys.exit()

_CONFIG_FILE = "config.env"

if os.path.isfile(_CONFIG_FILE):
    _LOG.info("%s Found and loading ...", _CONFIG_FILE)
    load_dotenv(_CONFIG_FILE)

if os.environ.get("_____REMOVE_____THIS_____LINE_____", None):
    _LOG.error("Please remove the line mentioned in the first hashtag from the config.env file")
    sys.exit()


class Config:
    """ Configs to setup Userge """
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH", None)
    WORKERS = int(os.environ.get("WORKERS", 4))
    ANTISPAM_SENTRY = os.environ.get("ANTISPAM_SENTRY", "").lower() == "true"
    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    DB_URI = os.environ.get("DATABASE_URL", '')
    LANG = os.environ.get("PREFERRED_LANGUAGE", "en")
    DOWN_PATH = os.environ.get("DOWN_PATH", "downloads").rstrip('/') + '/'
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
    G_DRIVE_IS_TD = os.environ.get("G_DRIVE_IS_TD", "").lower() == "true"
    G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK", None)
    GOOGLE_CHROME_DRIVER = os.environ.get("GOOGLE_CHROME_DRIVER", None)
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN", None)
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/UsergeTeam/Userge")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    LOAD_UNOFFICIAL_PLUGINS = os.environ.get("LOAD_UNOFFICIAL_PLUGINS", "").lower() == "true"
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", '.')
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", '!')
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR", '█')
    UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR", '░')
    TMP_PATH = "userge/plugins/temp/"
    MAX_MESSAGE_LENGTH = 4096
    MSG_DELETE_TIMEOUT = 120
    WELCOME_DELETE_TIMEOUT = 120
    AUTOPIC_TIMEOUT = 300
    ALLOWED_CHATS = Filters.chat([])
    ALLOW_ALL_PMS = True
    USE_USER_FOR_CLIENT_CHECKS = False
    SUDO_USERS: Set[int] = set()
    ALLOWED_COMMANDS: Set[str] = set()
    UPSTREAM_REMOTE = 'upstream'
    HEROKU_APP = None
    HEROKU_GIT_URL = None


if not Config.LOG_CHANNEL_ID:
    _LOG.error("Need LOG_CHANNEL_ID !, Exiting ...")
    sys.exit()

if Config.SUDO_TRIGGER == Config.CMD_TRIGGER:
    _LOG.info("Invalid SUDO_TRIGGER!, You can't use `%s` as SUDO_TRIGGER", Config.CMD_TRIGGER)
    sys.exit()

if not os.path.isdir(Config.DOWN_PATH):
    _LOG.info("Creating Download Path...")
    os.mkdir(Config.DOWN_PATH)

if Config.HEROKU_API_KEY:
    _LOG.info("Checking Heroku App...")
    for heroku_app in heroku3.from_key(Config.HEROKU_API_KEY).apps():
        if (heroku_app and Config.HEROKU_APP_NAME
                and heroku_app.name == Config.HEROKU_APP_NAME):
            _LOG.info("Heroku App : %s Found...", heroku_app.name)
            Config.HEROKU_APP = heroku_app
            Config.HEROKU_GIT_URL = heroku_app.git_url.replace(
                "https://", "https://api:" + Config.HEROKU_API_KEY + "@")
            if not os.path.isdir(os.path.join(os.getcwd(), '.git')):
                tmp_heroku_git_path = os.path.join(os.getcwd(), 'tmp_heroku_git')
                _LOG.info("Cloning Heroku GIT...")
                Repo.clone_from(Config.HEROKU_GIT_URL, tmp_heroku_git_path)
                shutil.move(os.path.join(tmp_heroku_git_path, '.git'), os.getcwd())
                shutil.rmtree(tmp_heroku_git_path)
            break

_LOG.info("Checking REPO...")
try:
    _REPO = Repo()
except InvalidGitRepositoryError:
    _REPO = Repo.init()
if Config.UPSTREAM_REMOTE not in _REPO.remotes:
    _REPO.create_remote(Config.UPSTREAM_REMOTE, Config.UPSTREAM_REPO)
try:
    _REPO.remote(Config.UPSTREAM_REMOTE).fetch()
except GitCommandError as error:
    _LOG.error(error)
    sys.exit()

if not os.path.exists('bin'):
    _LOG.info("Creating BIN...")
    os.mkdir('bin')

_BINS = {
    "https://raw.githubusercontent.com/yshalsager/megadown/master/megadown":
    "bin/megadown",
    "https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py":
    "bin/cmrudl"}

_LOG.info("Checking BINs...")
for binary, path in _BINS.items():
    if not os.path.exists(path):
        _LOG.debug("Downloading %s...", binary)
        downloader = SmartDL(binary, path, progress_bar=False)
        downloader.start()

if Config.LOAD_UNOFFICIAL_PLUGINS:
    _LOG.info("Loading UnOfficial Plugins...")
    _CMDS = ["git clone --depth=1 https://github.com/UsergeTeam/Userge-Plugins.git",
             "pip3 install -U pip",
             "pip3 install -r Userge-Plugins/requirements.txt",
             "rm -rf userge/plugins/unofficial/",
             "mv Userge-Plugins/plugins/ userge/plugins/unofficial/",
             "cp -r Userge-Plugins/resources/* resources/",
             "rm -rf Userge-Plugins/"]
    os.system(" && ".join(_CMDS))  # nosec
    _LOG.info("UnOfficial Plugins Loaded Successfully!")


def get_version() -> str:
    """ get userge version """
    ver = f"{versions.__major__}.{versions.__minor__}.{versions.__micro__}"
    if "/usergeteam/userge" in Config.UPSTREAM_REPO.lower():
        stable = (getattr(versions, '__stable__', None)
                  or f"{versions.__major__}.{versions.__minor__}.{versions.__micro__ - 1}")
        diff = list(_REPO.iter_commits(f'v{stable}..HEAD'))
        if diff:
            return f"{ver}-staging.{len(diff)}"
    else:
        diff = list(_REPO.iter_commits(f'{Config.UPSTREAM_REMOTE}/master..HEAD'))
        if diff:
            return f"{ver}-custom.{len(diff)}"
    return ver
