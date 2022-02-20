# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Userge']

import asyncio
import functools
import importlib
import inspect
import os
import signal
import threading
import time
from contextlib import suppress
from types import ModuleType
from typing import List, Awaitable, Any, Optional, Union

from pyrogram import idle, types
from pyrogram.methods import Methods as RawMethods

from userge import logging, config
from userge.utils import time_formatter
from userge.utils.exceptions import UsergeBotNotFound
from .database import get_collection
from .ext import RawClient
from .methods import Methods

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  #####  %s  #####  !>>>"


def _import_module(path: str) -> Optional[ModuleType]:
    try:
        return importlib.import_module(path)
    except Exception as i_e:
        _LOG.error(_LOG_STR, f"[{path}] - {i_e}")


def _reload_module(module: Optional[ModuleType]) -> Optional[ModuleType]:
    if module:
        try:
            return importlib.reload(module)
        except Exception as i_e:
            _LOG.error(_LOG_STR, i_e)
            return module


class _Module:
    def __init__(self, cat: str, name: str):
        self.cat = cat
        self.name = name
        self._path = f"userge.plugins.{cat}.{name}"
        self._init: Optional[ModuleType] = None
        self._main: Optional[ModuleType] = None

    def init(self) -> Optional[ModuleType]:
        self._init = _import_module(self._path)

        return self._init

    def main(self) -> None:
        self._main = _import_module(self._path + ".__main__")

    def reload_init(self) -> Optional[ModuleType]:
        self._init = _reload_module(self._init)

        return self._init

    def reload_main(self) -> None:
        self._main = _reload_module(self._main)


_MODULES: List[_Module] = []
_START_TIME = time.time()
_USERGE_STATUS = get_collection("USERGE_STATUS")


async def _set_running(is_running: bool) -> None:
    await _USERGE_STATUS.update_one(
        {'_id': 'USERGE_STATUS'},
        {"$set": {'is_running': is_running}},
        upsert=True
    )


async def _is_running() -> bool:
    if config.ASSERT_SINGLE_INSTANCE:
        data = await _USERGE_STATUS.find_one({'_id': 'USERGE_STATUS'})
        if data:
            return bool(data['is_running'])

    return False


class _AbstractUserge(Methods, RawClient):
    def __init__(self, **kwargs) -> None:
        self._me: Optional[types.User] = None
        super().__init__(**kwargs)

    @property
    def id(self) -> int:
        """ returns client id """
        if self.is_bot:
            return RawClient.BOT_ID

        return RawClient.USER_ID

    @property
    def is_bot(self) -> bool:
        """ returns client is bot or not """
        if self._bot is not None:
            return hasattr(self, 'ubot')

        return bool(config.BOT_TOKEN)

    @property
    def uptime(self) -> str:
        """ returns userge uptime """
        return time_formatter(time.time() - _START_TIME)

    async def _load_plugins(self) -> None:
        _LOG.info(_LOG_STR, "Importing All Plugins")

        _MODULES.clear()
        base = os.path.join("userge", "plugins")

        for cat in os.listdir(base):
            cat_path = os.path.join(base, cat)
            if not os.path.isdir(cat_path) or cat.startswith("_"):
                continue

            for plg in os.listdir(cat_path):
                plg_path = os.path.join(cat_path, plg)
                if not os.path.isdir(plg_path) or plg.startswith("_"):
                    continue

                mdl = _Module(cat, plg)
                mt = mdl.init()
                if mt:
                    _MODULES.append(mdl)
                    self.manager.update_plugin(mt.__name__, mt.__doc__)

        for mdl in _MODULES:
            mdl.main()

        await self.manager.init()
        _LOG.info(_LOG_STR, f"Imported ({len(_MODULES)}) Plugins => "
                  + str(['.'.join((mdl.cat, mdl.name)) for mdl in _MODULES]))

    async def reload_plugins(self) -> int:
        """ Reload all Plugins """
        _LOG.info(_LOG_STR, "Reloading All Plugins")

        self.manager.clear_plugins()
        reloaded: List[_Module] = []

        for mdl in _MODULES:
            if mdl.reload_init():
                reloaded.append(mdl)

        for mdl in reloaded:
            mdl.reload_main()

        await self.manager.init()
        _LOG.info(_LOG_STR, f"Reloaded {len(reloaded)} Plugins => "
                  + str([mdl.name for mdl in reloaded]))

        return len(reloaded)

    async def get_me(self, cached: bool = True) -> types.User:
        if not cached or self._me is None:
            self._me = await super().get_me()

        return self._me

    async def start(self):
        await super().start()
        self._me = await self.get_me()

        if self.is_bot:
            RawClient.BOT_ID = self._me.id
        else:
            RawClient.USER_ID = self._me.id

    def __eq__(self, o: object) -> bool:
        return isinstance(o, _AbstractUserge) and self.id == o.id

    def __hash__(self) -> int:  # pylint: disable=W0235
        return super().__hash__()


class UsergeBot(_AbstractUserge):
    """ UsergeBot, the bot """
    def __init__(self, **kwargs) -> None:
        super().__init__(session_name=":memory:", **kwargs)

    @property
    def ubot(self) -> 'Userge':
        """ returns userbot """
        return self._bot


class Userge(_AbstractUserge):
    """ Userge, the userbot """

    has_bot = bool(config.BOT_TOKEN)

    def __init__(self, **kwargs) -> None:
        kwargs = {
            'api_id': config.API_ID,
            'api_hash': config.API_HASH,
            'workers': config.WORKERS
        }

        if config.BOT_TOKEN:
            kwargs['bot_token'] = config.BOT_TOKEN

        if config.SESSION_STRING and config.BOT_TOKEN:
            RawClient.DUAL_MODE = True
            kwargs['bot'] = UsergeBot(bot=self, **kwargs)

        kwargs['session_name'] = config.SESSION_STRING or ":memory:"
        super().__init__(**kwargs)

    @property
    def dual_mode(self) -> bool:
        return RawClient.DUAL_MODE

    @property
    def bot(self) -> Union['UsergeBot', 'Userge']:
        """ returns usergebot """
        if self._bot is None:
            if config.BOT_TOKEN:
                return self
            raise UsergeBotNotFound("Need BOT_TOKEN ENV!")

        return self._bot

    async def start(self) -> None:
        """ start client and bot """
        counter = 0
        timeout = 30  # 30 sec
        max_ = 1800  # 30 min

        while await _is_running():
            _LOG.info(_LOG_STR, "Waiting for the Termination of "
                                f"previous Userge instance ... [{timeout} sec]")
            time.sleep(timeout)

            counter += timeout
            if counter >= max_:
                _LOG.info(_LOG_STR, f"Max timeout reached ! [{max_} sec]")
                break

        _LOG.info(_LOG_STR, "Starting Userge")
        await _set_running(True)
        await super().start()

        if self._bot is not None:
            _LOG.info(_LOG_STR, "Starting UsergeBot")
            await self._bot.start()

        await self._load_plugins()
        await self.manager.start()

    async def stop(self) -> None:  # pylint: disable=arguments-differ
        """ stop client and bot """
        await self.manager.stop()

        if self._bot is not None:
            _LOG.info(_LOG_STR, "Stopping UsergeBot")
            await self._bot.stop()

        _LOG.info(_LOG_STR, "Stopping Userge")

        await super().stop()
        await _set_running(False)

    def begin(self, coro: Optional[Awaitable[Any]] = None) -> None:
        """ start userge """
        lock = asyncio.Lock()
        loop_is_stopped = asyncio.Event()
        running_tasks: List[asyncio.Task] = []

        async def _waiter() -> None:
            with suppress(asyncio.exceptions.TimeoutError):
                await asyncio.wait_for(loop_is_stopped.wait(), 30)

        async def _finalize() -> None:
            async with lock:
                for t in running_tasks:
                    t.cancel()
                if self.is_initialized:
                    await self.stop()

            # pylint: disable=expression-not-assigned
            [t.cancel() for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            await self.loop.shutdown_asyncgens()

            self.loop.stop()
            _LOG.info(_LOG_STR, "Loop Stopped !")
            loop_is_stopped.set()

        async def _shutdown(_sig: signal.Signals) -> None:
            _LOG.info(_LOG_STR, f"Received Stop Signal [{_sig.name}], Exiting Userge ...")
            await _finalize()

        for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
            self.loop.add_signal_handler(
                sig, lambda _sig=sig: self.loop.create_task(_shutdown(_sig)))

        try:
            self.loop.run_until_complete(self.start())
        except RuntimeError:
            return

        for task in self._tasks:
            running_tasks.append(self.loop.create_task(task()))

        mode = "[DUAL]" if RawClient.DUAL_MODE else "[BOT]" if config.BOT_TOKEN else "[USER]"

        with suppress(asyncio.exceptions.CancelledError, RuntimeError):
            if coro:
                _LOG.info(_LOG_STR, f"Running Coroutine - {mode}")
                self.loop.run_until_complete(coro)
            else:
                _LOG.info(_LOG_STR, f"Idling Userge - {mode}")
                idle()
            self.loop.run_until_complete(_finalize())

        with suppress(RuntimeError):
            self.loop.run_until_complete(_waiter())


def _un_wrapper(obj, name, function):
    loop = asyncio.get_event_loop()

    @functools.wraps(function)
    def _wrapper(*args, **kwargs):
        coroutine = function(*args, **kwargs)
        if (threading.current_thread() is not threading.main_thread()
                and inspect.iscoroutine(coroutine)):
            async def _():
                return await asyncio.wrap_future(asyncio.run_coroutine_threadsafe(coroutine, loop))
            return _()
        return coroutine

    setattr(obj, name, _wrapper)


def _un_wrap(source):
    for name in dir(source):
        if name.startswith("_"):
            continue
        wrapped = getattr(getattr(source, name), '__wrapped__', None)
        if wrapped and (inspect.iscoroutinefunction(wrapped)
                        or inspect.isasyncgenfunction(wrapped)):
            _un_wrapper(source, name, wrapped)


_un_wrap(RawMethods)
for class_name in dir(types):
    cls = getattr(types, class_name)
    if inspect.isclass(cls):
        _un_wrap(cls)
