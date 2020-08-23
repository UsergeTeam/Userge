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
        self.doc: Optional[str] = None
        self.commands: List['command.Command'] = []
        self.filters: List['_filter.Filter'] = []
        _LOG.debug(_LOG_STR, f"created plugin -> {self.name}")

    def __repr__(self) -> str:
        return f"<plugin {self.name} {self.commands + self.filters}>"

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

    async def init(self) -> None:
        """ initialize the plugin """
        await asyncio.gather(*[flt.init() for flt in self.commands + self.filters])

    def add(self, obj: Union['command.Command', '_filter.Filter']) -> None:
        """ add command or filter to plugin """
        obj.plugin_name = self.name
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

    async def enable(self) -> List[str]:
        """ enable all commands in the plugin """
        if self.is_enabled:
            return []
        return await _do_it(self, 'enable')

    async def disable(self) -> List[str]:
        """ disable all commands in the plugin """
        if not self.is_enabled:
            return []
        return await _do_it(self, 'disable')

    async def load(self) -> List[str]:
        """ load all commands in the plugin """
        if self.is_loaded:
            return []
        return await _do_it(self, 'load')

    async def unload(self) -> List[str]:
        """ unload all commands in the plugin """
        if not self.is_loaded:
            return []
        return await _do_it(self, 'unload')


async def _do_it(plg: Plugin, work_type: str) -> List[str]:
    done: List[str] = []
    for flt in plg.commands + plg.filters:
        tmp = await getattr(flt, work_type)()
        if tmp:
            done.append(tmp)
    if done:
        _LOG.info(_LOG_STR, f"{work_type.rstrip('e')}ed {plg}")
    return done
