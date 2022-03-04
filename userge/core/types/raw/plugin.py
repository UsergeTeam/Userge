# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Plugin']

import asyncio
from typing import Union, List, Optional, Callable, Awaitable, Any

from userge import logging
from . import command, filter as _filter  # pylint: disable=unused-import
from ... import client as _client  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)

_LOADED = 0
_UNLOADED = 1


class Plugin:
    """ plugin class """
    def __init__(self, client: '_client.Userge', cat: str, name: str) -> None:
        self._client = client
        self.cat = cat
        self.name = name
        self.doc: str = "undefined"
        self.commands: List['command.Command'] = []
        self.filters: List['_filter.Filter'] = []

        self._state = _UNLOADED

        self._tasks_todo: List[Callable[[], Awaitable[Any]]] = []
        self._running_tasks: List[asyncio.Task] = []

        self._on_start_callback: Optional[Callable[[], Awaitable[Any]]] = None
        self._on_stop_callback: Optional[Callable[[], Awaitable[Any]]] = None
        self._on_exit_callback: Optional[Callable[[], Awaitable[Any]]] = None

    def __repr__(self) -> str:
        return f"<plugin {self.name} {self.commands + self.filters}>"

    @property
    def loaded(self) -> bool:
        """ returns load status """
        return any((flt.loaded for flt in self.commands + self.filters))

    @property
    def loaded_commands(self) -> List['command.Command']:
        """ returns all loaded commands """
        return [cmd for cmd in self.commands if cmd.loaded]

    @property
    def unloaded_commands(self) -> List['command.Command']:
        """ returns all unloaded commands """
        return [cmd for cmd in self.commands if not cmd.loaded]

    @property
    def loaded_filters(self) -> List['_filter.Filter']:
        """ returns all loaded filters """
        return [flt for flt in self.filters if flt.loaded]

    @property
    def unloaded_filters(self) -> List['_filter.Filter']:
        """ returns all unloaded filters """
        return [flt for flt in self.filters if not flt.loaded]

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

    def get_commands(self) -> List[str]:
        """ returns all sorted command names in the plugin """
        return sorted((cmd.name for cmd in self.loaded_commands))

    async def _start(self) -> None:
        if self._on_start_callback:
            await self._on_start_callback()

        self._running_tasks.clear()

        for todo in self._tasks_todo:
            self._running_tasks.append(asyncio.create_task(todo()))

        self._state = _LOADED

    async def _stop(self) -> None:
        for task in self._running_tasks:
            task.cancel()

        self._running_tasks.clear()

        if self._on_stop_callback:
            await self._on_stop_callback()

        self._state = _UNLOADED

    async def start(self) -> None:
        if self.loaded:
            await self._start()

    async def stop(self) -> None:
        if self._state == _LOADED:
            await self._stop()

    async def update(self) -> None:
        if self.loaded:
            if self._state == _UNLOADED:
                await self._start()
        else:
            if self._state == _LOADED:
                await self._stop()

    def clear(self) -> None:
        if self._state == _LOADED:
            raise AssertionError

        self.commands.clear()
        self.filters.clear()
        self._tasks_todo.clear()

        self._on_start_callback = None
        self._on_stop_callback = None
        self._on_exit_callback = None

    async def exit(self) -> None:
        if self._state == _LOADED:
            raise AssertionError

        if self._on_exit_callback:
            await self._on_exit_callback()

        self.clear()

    async def load(self) -> List[str]:
        """ load all commands in the plugin """
        if self._state == _LOADED:
            return []

        await self._start()
        return _do_it(self, 'load')

    async def unload(self) -> List[str]:
        """ unload all commands in the plugin """
        if self._state == _UNLOADED:
            return []

        out = _do_it(self, 'unload')
        await self._stop()

        return out

    def add_task(self, task: Callable[[], Awaitable[Any]]) -> None:
        self._tasks_todo.append(task)

    def set_on_start_callback(self, callback: Callable[[], Awaitable[Any]]) -> None:
        self._on_start_callback = callback

    def set_on_stop_callback(self, callback: Callable[[], Awaitable[Any]]) -> None:
        self._on_stop_callback = callback

    def set_on_exit_callback(self, callback: Callable[[], Awaitable[Any]]) -> None:
        self._on_exit_callback = callback


def _do_it(plg: Plugin, work_type: str) -> List[str]:
    done: List[str] = []

    for flt in plg.commands + plg.filters:
        tmp = getattr(flt, work_type)()
        if tmp:
            done.append(tmp)

    if done:
        _LOG.info(f"{work_type.rstrip('e')}ed {plg}")

    return done
