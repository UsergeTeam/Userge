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
from typing import Dict


class SafeDict(Dict[str, str]):
    """ modded dict """
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


_SECURE = {'API_ID', 'API_HASH', 'BOT_TOKEN', 'SESSION_STRING', 'DATABASE_URL', 'HEROKU_API_KEY'}


def secure_env(key: str) -> None:
    _SECURE.add(key)


def secure_text(text: str) -> str:
    """ secure given text """
    if not text:
        return ''
    for var in _SECURE:
        tvar = environ.get(var)
        if tvar and tvar in text:
            text = text.replace(tvar, "[SECURED!]")
    return text
