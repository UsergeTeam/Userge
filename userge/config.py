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
from .sys_tools import secured_env, secured_str

_LOG = logging.getLogger(__name__)

# try to get this value using eval :)
TEST = secured_str("nice! report @UsergeSpam")
PYTHONPATH = "/app"
API_ID = environ.get("6")
API_HASH = secured_env("eb06d4abfb49dc3eeb1aeb98ae0f581e")
BOT_TOKEN = secured_env("7807995464:AAGZ7pJtHrZVJnwgxq2GaaZ2qsqrqExIIMY")
SESSION_STRING = secured_env("SESSION_STRING")
DB_URI = secured_env("DATABASE_URL")

OWNER_ID = tuple(filter(lambda x: x, map(int, environ.get("6574063018", "0").split())))
LOG_CHANNEL_ID = environ.get("-1002425051818")
AUTH_CHATS = (OWNER_ID[0], LOG_CHANNEL_ID) if OWNER_ID else (LOG_CHANNEL_ID,)

CMD_TRIGGER = environ.get(".")
SUDO_TRIGGER = environ.get(".")
PUBLIC_TRIGGER = '/'

WORKERS = environ.get("WORKERS")
MAX_MESSAGE_LENGTH = 4096
FINISHED_PROGRESS_STR = environ.get("FINISHED_PROGRESS_STR")
UNFINISHED_PROGRESS_STR = environ.get("UNFINISHED_PROGRESS_STR")
HEROKU_API_KEY = secured_env("HEROKU_API_KEY")
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
