# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

""" setup gban """

from os import environ
from typing import Dict

WHITE_CACHE: Dict[int, str] = {}
FBAN_CHAT_ID = int(environ.get("FBAN_CHAT_ID") or 0)


async def is_whitelist(user_id: int) -> bool:
    return user_id in WHITE_CACHE
