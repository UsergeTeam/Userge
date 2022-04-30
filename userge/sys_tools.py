# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.
#
# noqa
# skipcq

import sys
from os import environ
from typing import Dict, Optional


_CACHE: Dict[str, str] = {}


def secured_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """ get secured env """
    if not key:
        raise ValueError

    try:
        value = environ.pop(key)
    except KeyError:
        if key in _CACHE:
            return _CACHE[key]
        value = default

    ret: Optional[str] = None

    if value:
        ret = _CACHE[key] = secured_str(value)

    return ret


def secured_str(value: str) -> str:
    """ get secured string """
    if not value:
        raise ValueError

    if isinstance(value, _SafeStr):
        return value

    ret = _SafeStr(_ST)
    ret._ = value

    return ret


class SafeDict(Dict[str, str]):
    """ modded dict """
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


class _SafeMeta(type):
    def __new__(mcs, *__):
        for _ in filter(lambda _: (
                _.startswith('_') and _.__ne__('__new__')
                and not __[2].__contains__(_)), __[1][0].__dict__):
            __[2][_] = lambda _, *__, ___=_: _._.__getattribute__(___)(*__)
        return type.__new__(mcs, *__)


class _SafeStr(str, metaclass=_SafeMeta):
    def __setattr__(self, *_):
        if _[0].__eq__('_') and not hasattr(self, '_'):
            super().__setattr__(*_)

    def __delattr__(self, _):
        pass

    def __getattribute__(self, _):
        ___ = lambda _, __=_: _.__getattribute__(__) if __.__ne__('_') else _
        _ = getattr(sys, '_getframe')(1)
        while _:
            _f, _n = _.f_code.co_filename, _.f_code.co_name
            if _f.__contains__("exec") or _f.__eq__("<string>") and _n.__ne__("<module>"):
                return ___(_ST)
            if _f.__contains__("asyncio") and _n.__eq__("_run"):
                __ = getattr(getattr(_.f_locals['self'], '_callback').__self__, '_coro').cr_frame
                _f, _n = __.f_code.co_filename, __.f_code.co_name
                if (_f.__contains__("dispatcher") and _n.__eq__("handler_worker") or
                        (_f.__contains__("client") or _f.__contains__("plugin")) and
                        ("start", "stop").__contains__(_n)):
                    break
                return ___(_ST)
            _ = _.f_back
        return ___(super().__getattribute__('_'))

    def __repr__(self):
        return self

    def __str__(self):
        return self


_ST = "[SECURED!]"
