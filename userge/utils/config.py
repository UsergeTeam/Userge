# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import heroku3
from dotenv import load_dotenv
from .logger import logging

LOG = logging.getLogger(__name__)

CONFIG_FILE = "config.env"

if os.path.isfile(CONFIG_FILE):
    LOG.info(f"{CONFIG_FILE} Found and loading ...")
    load_dotenv(CONFIG_FILE)

if os.environ.get("_____REMOVE_____THIS_____LINE_____", None):
    LOG.error("Please remove the line mentioned in the first hashtag from the config.env file")
    quit(1)


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

    DOWN_PATH = "./downloads/"

    SCREENSHOT_API = os.environ.get("SCREENSHOT_API", None)

    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID", None)

    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET", None)

    G_DRIVE_PARENT_ID = os.environ.get("G_DRIVE_PARENT_ID", None)

    G_DRIVE_IS_TD = bool(os.environ.get("G_DRIVE_IS_TD", False))

    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))

    OFFICIAL_REPO_LINK = "https://github.com/UsergeTeam/Userge"

    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)

    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)

    HEROKU_APP = None

    HEROKU_GIT_URL = None

    MSG_DELETE_TIMEOUT = 10


if not os.path.isdir(Config.DOWN_PATH):
    LOG.info("Creating Download Path...")
    os.makedirs(Config.DOWN_PATH)


if Config.HEROKU_API_KEY:
    LOG.info("Checking Heroku App...")

    for heroku_app in heroku3.from_key(Config.HEROKU_API_KEY).apps():
        if heroku_app and Config.HEROKU_APP_NAME and \
            heroku_app.name == Config.HEROKU_APP_NAME:

            LOG.info(f"Heroku App : {heroku_app.name} Found...")

            Config.HEROKU_APP = heroku_app
            Config.HEROKU_GIT_URL = heroku_app.git_url.replace(
                "https://", "https://api:" + Config.HEROKU_API_KEY + "@")
            break