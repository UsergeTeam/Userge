# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import sys
import shutil
from typing import Set

import heroku3
from git import Repo
from pySmartDL import SmartDL
from dotenv import load_dotenv
from pyrogram import Filters

from userge import logging

LOG = logging.getLogger(__name__)

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOG.info("You MUST have a python version of at least 3.6 !")
    sys.exit()

CONFIG_FILE = "config.env"

if os.path.isfile(CONFIG_FILE):
    LOG.info("%s Found and loading ...", CONFIG_FILE)
    load_dotenv(CONFIG_FILE)

if os.environ.get("_____REMOVE_____THIS_____LINE_____", None):
    LOG.error("Please remove the line mentioned in the first hashtag from the config.env file")
    sys.exit()


class Config:
    """
    Configs to setup Userge.
    """

    API_ID = int(os.environ.get("API_ID", 12345))

    API_HASH = os.environ.get("API_HASH", None)

    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)

    DB_URI = os.environ.get("DATABASE_URL", None)

    MAX_MESSAGE_LENGTH = 4096

    LANG = os.environ.get("PREFERRED_LANGUAGE", "en")

    DOWN_PATH = os.environ.get("DOWN_PATH", "downloads/")

    SCREENSHOT_API = os.environ.get("SCREENSHOT_API", None)

    CURRENCY_API = os.environ.get("CURRENCY_API", None)

    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID", None)

    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET", None)

    G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID", None)

    G_DRIVE_IS_TD = bool(os.environ.get("G_DRIVE_IS_TD", False))

    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/UsergeTeam/Userge")

    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)

    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)

    HEROKU_APP = None

    HEROKU_GIT_URL = None

    PUSHING = False

    MSG_DELETE_TIMEOUT = 120

    WELCOME_DELETE_TIMEOUT = 120

    ALLOWED_CHATS = Filters.chat([])

    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", '!')

    SUDO_USERS: Set[int] = set()

    ALLOWED_COMMANDS: Set[str] = set()


if Config.SUDO_TRIGGER == '.':
    LOG.info("Invalid SUDO_TRIGGER!, You can't use `.` as SUDO_TRIGGER")
    sys.exit()

if not os.path.isdir(Config.DOWN_PATH):
    LOG.info("Creating Download Path...")
    os.mkdir(Config.DOWN_PATH)

if Config.HEROKU_API_KEY:
    LOG.info("Checking Heroku App...")

    for heroku_app in heroku3.from_key(Config.HEROKU_API_KEY).apps():
        if heroku_app and Config.HEROKU_APP_NAME and \
            heroku_app.name == Config.HEROKU_APP_NAME:

            LOG.info("Heroku App : %s Found...", heroku_app.name)

            Config.HEROKU_APP = heroku_app
            Config.HEROKU_GIT_URL = heroku_app.git_url.replace(
                "https://", "https://api:" + Config.HEROKU_API_KEY + "@")

            if not os.path.isdir(os.path.join(os.getcwd(), '.git')):
                tmp_heroku_git_path = os.path.join(os.getcwd(), 'tmp_heroku_git')

                LOG.info("Cloning Heroku GIT...")

                Repo.clone_from(Config.HEROKU_GIT_URL, tmp_heroku_git_path)
                shutil.move(os.path.join(tmp_heroku_git_path, '.git'), os.getcwd())
                shutil.rmtree(tmp_heroku_git_path)

            break

if not os.path.exists('bin'):
    LOG.info("Creating BIN...")
    os.mkdir('bin')

BINS = {
    "https://raw.githubusercontent.com/yshalsager/megadown/master/megadown":
    "bin/megadown",
    "https://raw.githubusercontent.com/yshalsager/cmrudl.py/master/cmrudl.py":
    "bin/cmrudl"}

LOG.info("Downloading BINs...")

for binary, path in BINS.items():
    LOG.debug("Downloading %s...", binary)
    downloader = SmartDL(binary, path, progress_bar=False)
    downloader.start()
    os.chmod(path, 0o755)
