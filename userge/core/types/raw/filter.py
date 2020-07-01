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
from typing import List, Tuple, Callable, Any, Optional

from pyrogram.client.handlers.handler import Handler

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
                 client: '_client.Userge',
                 group: int,
                 allow_via_bot: bool) -> None:
        self._client = client
        self._group = group
        self._allow_via_bot = allow_via_bot
        self._enabled = True
        self._loaded = False
        self.name: str
        self.about: Optional[str]
        self._handler: Handler

    def __repr__(self) -> str:
        return f"<filter - {self.name}>"

    async def init(self) -> None:
        """ initialize the filter """
        self._enabled, loaded = _init(self.name)
        if loaded:
            await self.load()

    @property
    def allow_via_bot(self) -> bool:
        """ returns bot availability """
        return self._allow_via_bot

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

    def update(self, func: Callable[[Any], Any], handler: Handler) -> None:
        """ update filter """
        self.name = f"{func.__module__.split('.')[-1]}.{func.__name__}"
        self.about = func.__doc__
        self._handler = handler
        _LOG.debug(_LOG_STR, f"created filter -> {self.name}")

    async def enable(self) -> str:
        """ enable the filter """
        if self._enabled:
            return ''
        self._enabled = True
        await _enable(self.name)
        _LOG.debug(_LOG_STR, f"enabled filter -> {self.name}")
        return self.name

    async def disable(self) -> str:
        """ disable the filter """
        if not self._enabled:
            return ''
        self._enabled = False
        await _disable(self.name)
        _LOG.debug(_LOG_STR, f"disabled filter -> {self.name}")
        return self.name

    async def load(self) -> str:
        """ load the filter """
        if self._loaded:
            return ''
        self._client.add_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self._allow_via_bot and self._client._bot is not None:
            self._client._bot.add_handler(self._handler, self._group)
        self._loaded = True
        await _load(self.name)
        _LOG.debug(_LOG_STR, f"loaded filter -> {self.name}")
        return self.name

    async def unload(self) -> str:
        """ unload the filter """
        if not self._loaded:
            return ''
        self._client.remove_handler(self._handler, self._group)
        # pylint: disable=protected-access
        if self._allow_via_bot and self._client._bot is not None:
            self._client._bot.remove_handler(self._handler, self._group)
        self._loaded = False
        await _unload(self.name)
        _LOG.debug(_LOG_STR, f"unloaded filter -> {self.name}")
        return self.name
