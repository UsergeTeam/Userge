# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Manager']

import asyncio
import logging
from itertools import islice, chain
from typing import Union, List, Dict, Optional

from userge import config
from ..raw import Filter, Command, Plugin
from ... import client as _client, get_collection  # pylint: disable=unused-import

_LOG = logging.getLogger(__name__)
_FLT = Union[Filter, Command]


class Manager:
    """ manager for userge """
    def __init__(self, client: '_client.Userge') -> None:
        self._client = client
        self._event = asyncio.Event()
        self.plugins: Dict[str, Plugin] = {}

    @property
    def commands(self) -> Dict[str, Command]:
        """ returns all commands """
        return {cmd.name: cmd for plg in self.plugins.values() for cmd in plg.commands}

    @property
    def filters(self) -> Dict[str, Filter]:
        """ returns all filters """
        return {flt.name: flt for plg in self.plugins.values() for flt in plg.filters}

    @property
    def loaded_commands(self) -> Dict[str, Command]:
        """ returns all loaded commands """
        return {cmd.name: cmd for cmd in self.commands.values() if cmd.loaded}

    @property
    def unloaded_commands(self) -> List[Command]:
        """ returns all unloaded commands """
        return [cmd for cmd in self.commands.values() if not cmd.loaded]

    @property
    def loaded_filters(self) -> List[Filter]:
        """returns all loaded filters"""
        return [flt for flt in self.filters.values() if flt.loaded]

    @property
    def unloaded_filters(self) -> List[Filter]:
        """ returns all unloaded filters """
        return [flt for flt in self.filters.values() if not flt.loaded]

    @property
    def loaded_plugins(self) -> Dict[str, Plugin]:
        """ returns all loaded plugins """
        return {plg.name: plg for plg in self.plugins.values() if plg.loaded}

    @property
    def unloaded_plugins(self) -> List[Plugin]:
        """returns all unloaded plugins"""
        return [plg for plg in self.plugins.values() if not plg.loaded]

    def _get_plugin(self, cat: str, name: str) -> Plugin:
        plg = self.plugins[name] = Plugin(self._client, cat, name)
        return plg

    def get_plugin(self, module_name: str) -> Plugin:
        """ get plugin from manager """
        # __main__
        name = module_name.split('.')[-2]
        if name in self.plugins:
            return self.plugins[name]

        cat = module_name.split('.')[-3]

        return self._get_plugin(cat, name)

    def update_plugin(self, module_name: str, doc: Optional[str]) -> None:
        """ get plugin from name """
        # __init__
        cat, name = module_name.split('.')[-2:]
        if name not in self.plugins:
            self._get_plugin(cat, name)

        if doc:
            self.plugins[name].doc = doc.strip()

    def get_plugins(self) -> Dict[str, List[str]]:
        """ returns categorized enabled plugins """
        ret_dict: Dict[str, List[str]] = {}

        for plg in self.loaded_plugins.values():
            if plg.cat not in ret_dict:
                ret_dict[plg.cat] = []

            ret_dict[plg.cat].append(plg.name)

        return ret_dict

    def get_all_plugins(self) -> Dict[str, List[str]]:
        """ returns all categorized plugins """
        ret_dict: Dict[str, List[str]] = {}

        for plg in self.plugins.values():
            if plg.cat not in ret_dict:
                ret_dict[plg.cat] = []

            ret_dict[plg.cat].append(plg.name)

        return ret_dict

    async def load_commands(self, commands: List[str]) -> List[str]:
        """ load list of commands """
        loaded: List[str] = []

        for cmd_name in set(commands).intersection(set(self.commands)):
            ret = self.commands[cmd_name].load()
            if ret:
                loaded.append(ret)

        if loaded:
            await _load(loaded)
            await self._update()

        return loaded

    async def unload_commands(self, commands: List[str]) -> List[str]:
        """ unload list of commands """
        unloaded: List[str] = []

        for cmd_name in set(commands).intersection(set(self.commands)):
            ret = self.commands[cmd_name].unload()
            if ret:
                unloaded.append(ret)

        if unloaded:
            await _unload(unloaded)
            await self._update()

        return unloaded

    async def load_filters(self, filters: List[str]) -> List[str]:
        """ load list of filters """
        loaded: List[str] = []

        for flt_name in set(filters).intersection(set(self.filters)):
            ret = self.filters[flt_name].load()
            if ret:
                loaded.append(ret)

        if loaded:
            await _load(loaded)
            await self._update()

        return loaded

    async def unload_filters(self, filters: List[str]) -> List[str]:
        """ unload list of filters """
        unloaded: List[str] = []

        for flt_name in set(filters).intersection(set(self.filters)):
            ret = self.filters[flt_name].unload()
            if ret:
                unloaded.append(ret)

        if unloaded:
            await _unload(unloaded)
            await self._update()

        return unloaded

    async def load_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """ load list of plugins """
        loaded: Dict[str, List[str]] = {}

        for plg_name in set(plugins).intersection(set(self.plugins)):
            ret = await self.plugins[plg_name].load()
            if ret:
                loaded.update({plg_name: ret})

        to_save = [_ for _ in loaded.values() for _ in _]
        if to_save:
            await _load(to_save)

        return loaded

    async def unload_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """ unload list of plugins """
        unloaded: Dict[str, List[str]] = {}

        for plg_name in set(plugins).intersection(set(self.plugins)):
            ret = await self.plugins[plg_name].unload()
            if ret:
                unloaded.update({plg_name: ret})

        to_save = [_ for _ in unloaded.values() for _ in _]
        if to_save:
            await _unload(to_save)

        return unloaded

    async def _update(self) -> None:
        for plg in self.plugins.values():
            await plg.update()

    def remove(self, name) -> None:
        try:
            plg = self.plugins.pop(name)
            plg.clear()
        except KeyError:
            pass

    async def init(self) -> None:
        self._event.clear()
        await _init_unloaded()

        for plg in self.plugins.values():
            for flt in plg.commands + plg.filters:
                if _unloaded(flt.name):
                    continue

                flt.load()

    @property
    def should_wait(self) -> bool:
        return not self._event.is_set()

    async def wait(self) -> None:
        await self._event.wait()

    async def _do_plugins(self, meth: str) -> None:
        loop = asyncio.get_running_loop()
        data = iter(self.plugins.values())

        while True:
            chunk = islice(data, config.WORKERS)

            try:
                plg = next(chunk)
            except StopIteration:
                break

            tasks = []

            for plg in chain((plg,), chunk):
                tasks.append((plg, loop.create_task(getattr(plg, meth)())))

            for plg, task in tasks:
                try:
                    await task
                except Exception as i_e:
                    _LOG.error(f"({meth}) [{plg.cat}/{plg.name}] - {i_e}")

            tasks.clear()

        _LOG.info(f"on_{meth} tasks completed !")

    async def start(self) -> None:
        self._event.clear()
        await self._do_plugins('start')
        self._event.set()

    async def stop(self) -> None:
        self._event.clear()
        await self._do_plugins('stop')
        self._event.set()

    async def exit(self) -> None:
        await self._do_plugins('exit')
        self.plugins.clear()

    def clear(self) -> None:
        for plg in self.plugins.values():
            plg.clear()

        self.plugins.clear()

    @staticmethod
    async def clear_unloaded() -> bool:
        """ clear all unloaded filters in database """
        return await _clear_db()


_UNLOADED_FILTERS = get_collection("UNLOADED_FILTERS")
_UNLOADED: List[str] = []
_FLAG = False


async def _init_unloaded() -> None:
    global _FLAG  # pylint: disable=global-statement

    if not _FLAG:
        async for flt in _UNLOADED_FILTERS.find():
            _UNLOADED.append(flt['filter'])

        _FLAG = True


def _unloaded(name: str) -> bool:
    return _fix(name) in _UNLOADED


def _fix(name: str) -> str:
    return name.lstrip(config.CMD_TRIGGER)


async def _load(names: List[str]) -> None:
    to_delete = []

    for name in map(_fix, names):
        if name in _UNLOADED:
            _UNLOADED.remove(name)
            to_delete.append(name)

    if to_delete:
        await _UNLOADED_FILTERS.delete_many({'filter': {'$in': to_delete}})


async def _unload(names: List[str]) -> None:
    to_insert = []

    for name in map(_fix, names):
        if name == "load":
            continue

        if name not in _UNLOADED:
            _UNLOADED.append(name)
            to_insert.append(name)

    if to_insert:
        await _UNLOADED_FILTERS.insert_many(map(lambda _: dict(filter=_), to_insert))


async def _clear_db() -> bool:
    _UNLOADED.clear()
    await _UNLOADED_FILTERS.drop()

    return True
