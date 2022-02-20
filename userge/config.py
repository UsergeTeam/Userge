# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from os import environ

import heroku3

from userge import logging

_LOG = logging.getLogger(__name__)

API_ID = int(environ.get("API_ID"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")
SESSION_STRING = environ.get("SESSION_STRING")
DB_URI = environ.get("DATABASE_URL")

OWNER_ID = tuple(filter(lambda x: x, map(int, environ.get("OWNER_ID", "0").split())))
LOG_CHANNEL_ID = int(environ.get("LOG_CHANNEL_ID"))
AUTH_CHATS = (OWNER_ID[0], LOG_CHANNEL_ID) if OWNER_ID else (LOG_CHANNEL_ID,)

CMD_TRIGGER = environ.get("CMD_TRIGGER")
SUDO_TRIGGER = environ.get("SUDO_TRIGGER")
PUBLIC_TRIGGER = '/'

WORKERS = int(environ.get("WORKERS"))
MAX_MESSAGE_LENGTH = 4096

FINISHED_PROGRESS_STR = environ.get("FINISHED_PROGRESS_STR")
UNFINISHED_PROGRESS_STR = environ.get("UNFINISHED_PROGRESS_STR")

HEROKU_API_KEY = environ.get("HEROKU_API_KEY")
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME")
HEROKU_APP = heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME] \
    if HEROKU_API_KEY and HEROKU_APP_NAME else None

ASSERT_SINGLE_INSTANCE = environ.get("ASSERT_SINGLE_INSTANCE", '').lower() == "true"
IGNORE_VERIFIED_CHATS = True


class Dynamic:
    DOWN_PATH = environ.get("DOWN_PATH")

    MSG_DELETE_TIMEOUT = 120
    EDIT_SLEEP_TIMEOUT = 10

    USER_IS_PREFERRED = False
