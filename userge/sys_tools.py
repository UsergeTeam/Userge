# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import sys
from os import environ
from typing import Dict, Optional


class SafeDict(Dict[str, str]):
    """ modded dict """
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


class _SafeMeta(type):
    # skipcq # noqa
    def __new__(mcs, *__):
        _ = '__setattr__', '__delattr__'
        for _ in filter(lambda _: (
                _.startswith('_') and _.__ne__('__new__')
                and not __[2].__contains__(_)),
                tuple(__[1][0].__dict__) + _):
            __[2][_] = lambda _, *__, ___=_: _.__handle__(___, *__)
        return type.__new__(mcs, *__)


class _SafeStr(str, metaclass=_SafeMeta):
    # skipcq # noqa
    def __self__(self):
        return self

    def __handle__(self, *_):
        return getattr(super(), _[0])(*_[1:])

    def __getattribute__(self, ___):
        _ = getattr(sys, '_getframe')(1)
        while _:
            _f, _n = _.f_code.co_filename, _.f_code.co_name
            if _f.__contains__("exec") or _f.__eq__("<string>") and _n.__ne__("<module>"):
                return lambda *_, **__: _spt(___, *_)
            if _f.__contains__("asyncio") and _n.__eq__("_run"):
                __ = getattr(getattr(_.f_locals['self'], '_callback').__self__, '_coro').cr_frame
                _f, _n = __.f_code.co_filename, __.f_code.co_name
                if (___.__eq__("__handle__") and _f.__contains__("dispatcher")
                        and _n.__eq__("handler_worker") or _f.__contains__("client")):
                    break
                return lambda *_, **__: _spt(___, *_)
            _ = _.f_back
        return super().__getattribute__(___)

    def __repr__(self):
        return self.__self__()

    def __str__(self):
        return self.__self__()


def _spt(_, *__, ___="[SECURED!]"):
    # skipcq # noqa
    if _.__eq__("__self__") or not __:
        return ___
    _ = __[0]
    if ('__contains__', '__eq__', '__ge__', '__gt__',
            '__le__', '__lt__', '__ne__').__contains__(_):
        return True
    if _.__eq__('__len__'):
        return 1
    if _.__eq__('__iter__'):
        return iter(___)
    if _.__eq__('__getnewargs__'):
        return ___,
    return ___


def secured_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """ get secured env """
    if not key:
        raise ValueError

    try:
        value = environ.pop(key)
    except KeyError:
        value = default

    ret: Optional[_SafeStr] = None

    if value:
        ret = _SafeStr(value)

    return ret


def secured_str(value: str) -> str:
    """ get secured string """
    if not value:
        raise ValueError

    return _SafeStr(value)
