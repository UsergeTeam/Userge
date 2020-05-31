# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Manager']

from typing import Union, List, Dict

from ..types import Plugin, Filtr, Command, clear_db
from .. import client as _client

_FLT = Union[Filtr, Command]


class Manager:
    """manager for userge"""
    def __init__(self) -> None:
        self.plugins: Dict[str, Plugin] = {}

    @property
    def commands(self) -> Dict[str, Command]:
        """returns all commands"""
        return {cmd.name: cmd for _, i in self.plugins.items() for cmd in i.commands}

    @property
    def filters(self) -> Dict[str, Filtr]:
        """returns all filters"""
        return {flt.name: flt for _, i in self.plugins.items() for flt in i.filters}

    @property
    def enabled_commands(self) -> Dict[str, Command]:
        """returns all enabled commands"""
        return {cmd.name: cmd for _, cmd in self.commands.items() if cmd.is_enabled}

    @property
    def disabled_commands(self) -> List[Command]:
        """returns all disabled commands"""
        return [cmd for _, cmd in self.commands.items() if cmd.is_disabled]

    @property
    def loaded_commands(self) -> List[Command]:
        """returns all loaded commands"""
        return [cmd for _, cmd in self.commands.items() if cmd.is_loaded]

    @property
    def unloaded_commands(self) -> List[Command]:
        """returns all unloaded commands"""
        return [cmd for _, cmd in self.commands.items() if not cmd.is_loaded]

    @property
    def enabled_filters(self) -> List[Filtr]:
        """returns all enabled filters"""
        return [flt for _, flt in self.filters.items() if flt.is_enabled]

    @property
    def disabled_filters(self) -> List[Filtr]:
        """returns all disabled filters"""
        return [flt for _, flt in self.filters.items() if flt.is_disabled]

    @property
    def loaded_filters(self) -> List[Filtr]:
        """returns all loaded filters"""
        return [flt for _, flt in self.filters.items() if flt.is_loaded]

    @property
    def unloaded_filters(self) -> List[Filtr]:
        """returns all unloaded filters"""
        return [flt for _, flt in self.filters.items() if not flt.is_loaded]

    @property
    def enabled_plugins(self) -> Dict[str, Plugin]:
        """returns all enabled plugins"""
        return {plg.name: plg for _, plg in self.plugins.items() if plg.is_enabled}

    @property
    def disabled_plugins(self) -> List[Plugin]:
        """returns all disabled plugins"""
        return [plg for _, plg in self.plugins.items() if plg.is_disabled]

    @property
    def loaded_plugins(self) -> List[Plugin]:
        """returns all loaded plugins"""
        return [plg for _, plg in self.plugins.items() if plg.is_loaded]

    @property
    def unloaded_plugins(self) -> List[Plugin]:
        """returns all unloaded plugins"""
        return [plg for _, plg in self.plugins.items() if not plg.is_loaded]

    def add_plugin(self, client: '_client.Userge',
                   name: str, about: str = '') -> Plugin:
        """add plugin to manager"""
        if name in self.plugins:
            return self.plugins[name]
        plg = Plugin(client, name, about)
        self.plugins[name] = plg
        return plg

    def clear_plugins(self) -> None:
        """clear all plugins"""
        self.plugins.clear()

    def enable_commands(self, commands: List[str]) -> List[str]:
        """enable list of commands"""
        enabled: List[str] = []
        for cmd_name in list(set(commands).intersection(set(self.commands))):
            ret = self.commands[cmd_name].enable()
            if ret:
                enabled.append(ret)
        return enabled

    def disable_commands(self, commands: List[str]) -> List[str]:
        """disable list of commands"""
        disabled: List[str] = []
        for cmd_name in list(set(commands).intersection(set(self.commands))):
            ret = self.commands[cmd_name].disable()
            if ret:
                disabled.append(ret)
        return disabled

    def load_commands(self, commands: List[str]) -> List[str]:
        """load list of commands"""
        loaded: List[str] = []
        for cmd_name in list(set(commands).intersection(set(self.commands))):
            ret = self.commands[cmd_name].load()
            if ret:
                loaded.append(ret)
        return loaded

    def unload_commands(self, commands: List[str]) -> List[str]:
        """unload list of commands"""
        unloaded: List[str] = []
        for cmd_name in list(set(commands).intersection(set(self.commands))):
            ret = self.commands[cmd_name].unload()
            if ret:
                unloaded.append(ret)
        return unloaded

    def enable_filters(self, filters: List[str]) -> List[str]:
        """enable list of filters"""
        enabled: List[str] = []
        for flt_name in list(set(filters).intersection(set(self.filters))):
            ret = self.filters[flt_name].enable()
            if ret:
                enabled.append(ret)
        return enabled

    def disable_filters(self, filters: List[str]) -> List[str]:
        """disable list of filters"""
        disabled: List[str] = []
        for flt_name in list(set(filters).intersection(set(self.filters))):
            ret = self.filters[flt_name].disable()
            if ret:
                disabled.append(ret)
        return disabled

    def load_filters(self, filters: List[str]) -> List[str]:
        """load list of filters"""
        loaded: List[str] = []
        for flt_name in list(set(filters).intersection(set(self.filters))):
            ret = self.filters[flt_name].load()
            if ret:
                loaded.append(ret)
        return loaded

    def unload_filters(self, filters: List[str]) -> List[str]:
        """unload list of filters"""
        unloaded: List[str] = []
        for flt_name in list(set(filters).intersection(set(self.filters))):
            ret = self.filters[flt_name].unload()
            if ret:
                unloaded.append(ret)
        return unloaded

    def enable_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """enable list of plugins"""
        enabled: Dict[str, List[str]] = {}
        for plg_name in list(set(plugins).intersection(set(self.plugins))):
            ret = self.plugins[plg_name].enable()
            if ret:
                enabled.update({plg_name: ret})
        return enabled

    def disable_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """disable list of plugins"""
        disabled: Dict[str, List[str]] = {}
        for plg_name in list(set(plugins).intersection(set(self.plugins))):
            ret = self.plugins[plg_name].disable()
            if ret:
                disabled.update({plg_name: ret})
        return disabled

    def load_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """load list of plugins"""
        loaded: Dict[str, List[str]] = {}
        for plg_name in list(set(plugins).intersection(set(self.plugins))):
            ret = self.plugins[plg_name].load()
            if ret:
                loaded.update({plg_name: ret})
        return loaded

    def unload_plugins(self, plugins: List[str]) -> Dict[str, List[str]]:
        """unload list of plugins"""
        unloaded: Dict[str, List[str]] = {}
        for plg_name in list(set(plugins).intersection(set(self.plugins))):
            ret = self.plugins[plg_name].unload()
            if ret:
                unloaded.update({plg_name: ret})
        return unloaded

    @staticmethod
    def clear() -> bool:
        """clear all filters in database"""
        return bool(clear_db())
