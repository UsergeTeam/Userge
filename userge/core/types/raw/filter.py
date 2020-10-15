# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Filter', 'clear_db']

import asyncio
from typing import List, Tuple, Dict, Callable, Any, Optional, Union

from pyrogram import filters as rawfilters
from pyrogram.filters import Filter as RawFilter
from pyrogram.handlers import MessageHandler
from pyrogram.handlers.handler import Handler

from userge import logging, Config
from ... import client as _client, get_collection  # pylint: disable=unused-import

_DISABLED_FILTERS = get_collection("DISABLED_FILTERS")
_UNLOADED_FILTERS = get_collection("UNLOADED_FILTERS")
_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  [[[[[  %s  ]]]]]  !>>>"

_DISABLED: List[str] = []
_UNLOADED: List[str] = []


def _init(name: str) -> Tuple[bool, bool]:
    name = name.lstrip(Config.CMD_TRIGGER)
    enabled = True
    loaded = True
    if name in _DISABLED:
        enabled = False
    if name in _UNLOADED:
        loaded = False
    return enabled, loaded


async def _main() -> None:
    async for flt in _DISABLED_FILTERS.find():
        _DISABLED.append(flt['filter'])
    async for flt in _UNLOADED_FILTERS.find():
        _UNLOADED.append(flt['filter'])


async def _enable(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    if name in _DISABLED:
        _DISABLED.remove(name)
        await _DISABLED_FILTERS.delete_one({'filter': name})


async def _disable(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    if name != "enable":
        _DISABLED.append(name)
        await _DISABLED_FILTERS.insert_one({'filter': name})


async def _load(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    if name in _UNLOADED:
        _UNLOADED.remove(name)
        await _UNLOADED_FILTERS.delete_one({'filter': name})


async def _unload(name: str) -> None:
    name = name.lstrip(Config.CMD_TRIGGER)
    if name != "load":
        _UNLOADED.append(name)
        await _UNLOADED_FILTERS.insert_one({'filter': name})


async def clear_db() -> bool:
    """ clear filters in DB """
    _DISABLED.clear()
    _UNLOADED.clear()
    await _DISABLED_FILTERS.drop()
    await _UNLOADED_FILTERS.drop()
    _LOG.info(_LOG_STR, "cleared filter DB!")
    return True

asyncio.get_event_loop().run_until_complete(_main())


class Filter:
    """ filter class """
    def __init__(self,
                 filters: RawFilter,
                 client: '_client.Userge',
                 group: int,
                 scope: List[str],
                 only_admins: bool,
                 allow_via_bot: bool,
                 check_client: bool,
                 check_downpath: bool,
                 check_perm: bool,
                 check_change_info_perm: bool,
                 check_edit_perm: bool,
                 check_delete_perm: bool,
                 check_restrict_perm: bool,
                 check_promote_perm: bool,
                 check_invite_perm: bool,
                 check_pin_perm: bool,
                 name: str = '') -> None:
        self.filters = rawfilters.create(lambda _, __, ___: self.is_enabled) & filters
        self.name = name
        self.scope = scope
        self.only_admins = only_admins
        self.allow_via_bot = allow_via_bot
        self.check_client = check_client
        self.check_downpath = check_downpath
        self.check_perm = check_perm
        self.check_change_info_perm = check_change_info_perm
        self.check_edit_perm = check_edit_perm
        self.check_delete_perm = check_delete_perm
        self.check_restrict_perm = check_restrict_perm
        self.check_promote_perm = check_promote_perm
        self.check_invite_perm = check_invite_perm
        self.check_pin_perm = check_pin_perm
        self.doc: Optional[str]
        self.plugin_name: str
        self._client = client
        self._group = group
        self._enabled = True
        self._loaded = False
        self._func: Callable[[Any], Any]
        self._handler: Handler

    @classmethod
    def parse(cls, **kwargs: Union[RawFilter, '_client.Userge', int, bool]) -> 'Filter':
        """ parse filter """
        return cls(**Filter._parse(**kwargs))  # pylint: disable=protected-access

    @staticmethod
    def _parse(allow_private: bool,
               allow_bots: bool,
               allow_groups: bool,
               allow_channels: bool,
               **kwargs: Union[RawFilter, '_client.Userge', int, bool]
               ) -> Dict[str, Union[RawFilter, '_client.Userge', int, bool]]:
        kwargs['check_client'] = kwargs['allow_via_bot'] and kwargs['check_client']
        kwargs['scope']: List[str] = []
        if allow_bots:
            kwargs['scope'].append('bot')
        if allow_private:
            kwargs['scope'].append('private')
        if allow_channels:
            kwargs['scope'].append('channel')
        if allow_groups:
            kwargs['scope'] += ['group', 'supergroup']
        kwargs['check_perm'] = kwargs['check_change_info_perm'] \
            or kwargs['check_edit_perm'] or kwargs['check_delete_perm'] \
            or kwargs['check_restrict_perm'] or kwargs['check_promote_perm'] \
            or kwargs['check_invite_perm'] or kwargs['check_pin_perm']
        return kwargs

    def __repr__(self) -> str:
        return f"<filter {self.name}>"

    @property
    def is_enabled(self) -> bool:
        """ returns enable status """
        return self._loaded and self._enabled

    @property
    def is_disabled(self) -> bool:
        """ returns disable status """
        return self._loaded and not self._enabled

    @property
    def is_loaded(self) -> bool:
        """ returns load status """
        return self._loaded

    async def init(self) -> None:
        """ initialize the filter """
        self._enabled, loaded = _init(self.name)
        if loaded:
            await self.load()

    def update(self, func: Callable[[Any], Any], template: Callable[[Any], Any]) -> None:
        """ update filter """
        if not self.name:
            self.name = f"{func.__module__.split('.')[-1]}.{func.__name__}"
        self.doc = func.__doc__.strip() if func.__doc__ else None
        self._func = func
        self._handler = MessageHandler(template, self.filters)
        _LOG.debug(_LOG_STR, f"updated {self}")

    async def enable(self) -> str:
        """ enable the filter """
        if self._enabled:
            return ''
        self._enabled = True
        await _enable(self.name)
        _LOG.debug(_LOG_STR, f"enabled {self}")
        return self.name

    async def disable(self) -> str:
        """ disable the filter """
        if not self._enabled:
            return ''
        self._enabled = False
        await _disable(self.name)
        _LOG.debug(_LOG_STR, f"disabled {self}")
        return self.name

    async def load(self) -> str:
        """ load the filter """
        if self._loaded or (self._client.is_bot and not self.allow_via_bot):
            return ''
        self._client.add_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self.allow_via_bot and self._client._bot is not None:
            self._client._bot.add_handler(self._handler, self._group)
        self._loaded = True
        await _load(self.name)
        _LOG.debug(_LOG_STR, f"loaded {self}")
        return self.name

    async def unload(self) -> str:
        """ unload the filter """
        if not self._loaded:
            return ''
        self._client.remove_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self.allow_via_bot and self._client._bot is not None:
            self._client._bot.remove_handler(self._handler, self._group)
        self._loaded = False
        await _unload(self.name)
        _LOG.debug(_LOG_STR, f"unloaded {self}")
        return self.name
