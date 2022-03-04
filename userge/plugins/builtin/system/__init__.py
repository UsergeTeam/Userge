# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

"""system related commands"""


from os import environ, getpid, kill
from typing import Set, Optional
try:
    from signal import CTRL_C_EVENT as SIGTERM
except ImportError:
    from signal import SIGTERM

from loader.userge import api
from userge import config

DISABLED_CHATS: Set[int] = set()


class Dynamic:
    DISABLED_ALL = False

    RUN_DYNO_SAVER = False
    STATUS = None


def get_env(key: str) -> Optional[str]:
    return environ.get(key)


async def set_env(key: str, value: str) -> None:
    environ[key] = value
    await api.set_env(key, value)

    if config.HEROKU_APP:
        config.HEROKU_APP.config()[key] = value


async def del_env(key: str) -> Optional[str]:
    if key in environ:
        val = environ.pop(key)
        await api.unset_env(key)

        if config.HEROKU_APP:
            del config.HEROKU_APP.config()[key]

        return val


def shutdown() -> None:
    if config.HEROKU_APP:
        config.HEROKU_APP.process_formation()['worker'].scale(0)

    kill(getpid(), SIGTERM)
