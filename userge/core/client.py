# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Userge']

import os
import sys
import time
import asyncio
import importlib
from types import ModuleType
from typing import List, Awaitable, Any, Optional

import psutil

from userge import logging, Config
from userge.utils import time_formatter
from userge.utils.exceptions import UsergeBotNotFound
from userge.plugins import get_all_plugins
from .methods import Methods
from .ext import RawClient

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  #####  %s  #####  !>>>"

_IMPORTED: List[ModuleType] = []
_INIT_TASKS: List[asyncio.Task] = []
_START_TIME = time.time()


async def _complete_init_tasks() -> None:
    if not _INIT_TASKS:
        return
    await asyncio.gather(*_INIT_TASKS)
    _INIT_TASKS.clear()


class _AbstractUserge(Methods, RawClient):
    @property
    def uptime(self) -> str:
        """ returns userge uptime """
        return time_formatter(time.time() - _START_TIME)

    async def finalize_load(self) -> None:
        """ finalize the plugins load """
        await asyncio.gather(_complete_init_tasks(), self.manager.init())

    async def load_plugin(self, name: str, reload_plugin: bool = False) -> None:
        """ Load plugin to Userge """
        _LOG.debug(_LOG_STR, f"Importing {name}")
        _IMPORTED.append(
            importlib.import_module(f"userge.plugins.{name}"))
        if reload_plugin:
            _IMPORTED[-1] = importlib.reload(_IMPORTED[-1])
        plg = _IMPORTED[-1]
        self.manager.update_plugin(plg.__name__, plg.__doc__)
        if hasattr(plg, '_init'):
            # pylint: disable=protected-access
            if asyncio.iscoroutinefunction(plg._init):
                _INIT_TASKS.append(
                    asyncio.get_event_loop().create_task(plg._init()))
        _LOG.debug(_LOG_STR, f"Imported {_IMPORTED[-1].__name__} Plugin Successfully")

    async def _load_plugins(self) -> None:
        _IMPORTED.clear()
        _INIT_TASKS.clear()
        _LOG.info(_LOG_STR, "Importing All Plugins")
        for name in get_all_plugins():
            try:
                await self.load_plugin(name)
            except ImportError as i_e:
                _LOG.error(_LOG_STR, i_e)
        await self.finalize_load()
        _LOG.info(_LOG_STR, f"Imported ({len(_IMPORTED)}) Plugins => "
                  + str([i.__name__ for i in _IMPORTED]))

    async def reload_plugins(self) -> int:
        """ Reload all Plugins """
        self.manager.clear_plugins()
        reloaded: List[str] = []
        _LOG.info(_LOG_STR, "Reloading All Plugins")
        for imported in _IMPORTED:
            try:
                reloaded_ = importlib.reload(imported)
            except ImportError as i_e:
                _LOG.error(_LOG_STR, i_e)
            else:
                reloaded.append(reloaded_.__name__)
        _LOG.info(_LOG_STR, f"Reloaded {len(reloaded)} Plugins => {reloaded}")
        await self.finalize_load()
        return len(reloaded)

    async def restart(self, update_req: bool = False) -> None:  # pylint: disable=arguments-differ
        """ Restart the AbstractUserge """
        _LOG.info(_LOG_STR, "Restarting Userge")
        await self.stop()
        try:
            c_p = psutil.Process(os.getpid())
            for handler in c_p.open_files() + c_p.connections():
                os.close(handler.fd)
        except Exception as c_e:  # pylint: disable=broad-except
            _LOG.error(_LOG_STR, c_e)
        if update_req:
            _LOG.info(_LOG_STR, "Installing Requirements...")
            os.system("pip3 install -U pip && pip3 install -r requirements.txt")  # nosec
        os.execl(sys.executable, sys.executable, '-m', 'userge')  # nosec
        sys.exit()


class _UsergeBot(_AbstractUserge):
    """ UsergeBot, the bot """
    def __init__(self, **kwargs) -> None:
        _LOG.info(_LOG_STR, "Setting UsergeBot Configs")
        super().__init__(session_name=":memory:", **kwargs)

    @property
    def ubot(self) -> 'Userge':
        """ returns userbot """
        return self._bot


class Userge(_AbstractUserge):
    """ Userge, the userbot """
    def __init__(self, **kwargs) -> None:
        _LOG.info(_LOG_STR, "Setting Userge Configs")
        if not (Config.HU_STRING_SESSION or Config.BOT_TOKEN):
            print("Need HU_STRING_SESSION or BOT_TOKEN, Exiting...")
            sys.exit()
        kwargs = {
            'api_id': Config.API_ID,
            'api_hash': Config.API_HASH,
            'workers': Config.WORKERS
        }
        if Config.BOT_TOKEN:
            if not Config.OWNER_ID:
                print("Need OWNER_ID, Exiting...")
                sys.exit()
            kwargs['bot_token'] = Config.BOT_TOKEN
        if Config.HU_STRING_SESSION and Config.BOT_TOKEN:
            RawClient.DUAL_MODE = True
            kwargs['bot'] = _UsergeBot(bot=self, **kwargs)
        kwargs['session_name'] = Config.HU_STRING_SESSION or ":memory:"
        super().__init__(**kwargs)

    @property
    def bot(self) -> '_UsergeBot':
        """ returns usergebot """
        if self._bot is None:
            raise UsergeBotNotFound("Need BOT_TOKEN ENV!")
        return self._bot

    async def start(self) -> None:
        """ start client and bot """
        _LOG.info(_LOG_STR, "Starting Userge")
        await super().start()
        if self._bot is not None:
            _LOG.info(_LOG_STR, "Starting UsergeBot")
            await self._bot.start()
        await self._load_plugins()

    async def stop(self) -> None:  # pylint: disable=arguments-differ
        """ stop client and bot """
        if self._bot is not None:
            _LOG.info(_LOG_STR, "Stopping UsergeBot")
            await self._bot.stop()
        _LOG.info(_LOG_STR, "Stopping Userge")
        await super().stop()

    def begin(self, coro: Optional[Awaitable[Any]] = None) -> None:
        """ start userge """
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete
        run(self.start())
        loop = asyncio.get_event_loop()
        running_tasks: List[asyncio.Task] = []
        for task in self._tasks:
            running_tasks.append(loop.create_task(task()))
        if coro:
            _LOG.info(_LOG_STR, "Running Coroutine")
            run(coro)
        else:
            _LOG.info(_LOG_STR, "Idling Userge")
            run(Userge.idle())
        _LOG.info(_LOG_STR, "Exiting Userge")
        for task in running_tasks:
            task.cancel()
        run(self.stop())
        for task in asyncio.all_tasks():
            task.cancel()
        run(loop.shutdown_asyncgens())
        loop.close()
