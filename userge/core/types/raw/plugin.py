# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Plugin']

import asyncio
from typing import Union, List, Optional

from userge import logging
from . import command, filter as _filter  # pylint: disable=unused-import
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  [[[[[  %s  ]]]]]  !>>>"


class Plugin:
    """ plugin class """
    def __init__(self, client: '_client.Userge', name: str, parent: str) -> None:
        self._client = client
        self.name = name
        self.parent = parent
        self.about: Optional[str]
        self.commands: List['command.Command'] = []
        self.filters: List['_filter.Filter'] = []
        _LOG.debug(_LOG_STR, f"created plugin -> {self.name}")

    def __repr__(self) -> str:
        return f"plugin {self.name} - {self.about} [{self.commands + self.filters}]"

    @property
    def is_enabled(self) -> bool:
        """ returns enable status """
        return any((flt.is_enabled for flt in self.commands + self.filters))

    @property
    def is_disabled(self) -> bool:
        """ returns disable status """
        return all((flt.is_disabled for flt in self.commands + self.filters))

    @property
    def is_loaded(self) -> bool:
        """ returns load status """
        return any((flt.is_loaded for flt in self.commands + self.filters))

    @property
    def enabled_commands(self) -> List['command.Command']:
        """ returns all enabled commands """
        return [cmd for cmd in self.commands if cmd.is_enabled]

    @property
    def disabled_commands(self) -> List['command.Command']:
        """ returns all disabled commands """
        return [cmd for cmd in self.commands if cmd.is_disabled]

    @property
    def loaded_commands(self) -> List['command.Command']:
        """ returns all loaded commands """
        return [cmd for cmd in self.commands if cmd.is_loaded]

    @property
    def unloaded_commands(self) -> List['command.Command']:
        """ returns all unloaded commands """
        return [cmd for cmd in self.commands if not cmd.is_loaded]

    @property
    def enabled_filters(self) -> List['_filter.Filter']:
        """ returns all enabled filters """
        return [flt for flt in self.filters if flt.is_enabled]

    @property
    def disabled_filters(self) -> List['_filter.Filter']:
        """ returns all disabled filters """
        return [flt for flt in self.filters if flt.is_disabled]

    @property
    def loaded_filters(self) -> List['_filter.Filter']:
        """ returns all loaded filters """
        return [flt for flt in self.filters if flt.is_loaded]

    @property
    def unloaded_filters(self) -> List['_filter.Filter']:
        """ returns all unloaded filters """
        return [flt for flt in self.filters if not flt.is_loaded]

    def add(self, obj: Union['command.Command', '_filter.Filter']) -> None:
        """ add command or filter to plugin """
        if isinstance(obj, command.Command):
            type_ = self.commands
        else:
            type_ = self.filters
        for flt in type_:
            if flt.name == obj.name:
                type_.remove(flt)
                break
        type_.append(obj)
        _LOG.debug(_LOG_STR, f"add filter to plugin -> {self.name}")

    def get_commands(self) -> List[str]:
        """ returns all sorted command names in the plugin """
        return sorted((cmd.name for cmd in self.enabled_commands))

    async def init(self) -> None:
        """ initialize the plugin """
        await asyncio.gather(*[flt.init() for flt in self.commands + self.filters])

    async def enable(self) -> List[str]:
        """ enable all commands in the plugin """
        if self.is_enabled:
            return []
        enabled: List[str] = []
        for flt in self.commands + self.filters:
            tmp = await flt.enable()
            if tmp:
                enabled.append(tmp)
        if enabled:
            _LOG.info(_LOG_STR, f"enabled plugin -> {self.name}")
        return enabled

    async def disable(self) -> List[str]:
        """ disable all commands in the plugin """
        if not self.is_enabled:
            return []
        disabled: List[str] = []
        for flt in self.commands + self.filters:
            tmp = await flt.disable()
            if tmp:
                disabled.append(tmp)
        if disabled:
            _LOG.info(_LOG_STR, f"disabled plugin -> {self.name}")
        return disabled

    async def load(self) -> List[str]:
        """ load all commands in the plugin """
        if self.is_loaded:
            return []
        loaded: List[str] = []
        for flt in self.commands + self.filters:
            tmp = await flt.load()
            if tmp:
                loaded.append(tmp)
        if loaded:
            _LOG.info(_LOG_STR, f"loaded plugin -> {self.name}")
        return loaded

    async def unload(self) -> List[str]:
        """ unload all commands in the plugin """
        if not self.is_loaded:
            return []
        unloaded: List[str] = []
        for flt in self.commands + self.filters:
            tmp = await flt.unload()
            if tmp:
                unloaded.append(tmp)
        if unloaded:
            _LOG.info(_LOG_STR, f"unloaded plugin -> {self.name}")
        return unloaded
