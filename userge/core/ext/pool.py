# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['submit_task', 'submit_thread', 'run_in_thread']

import asyncio
from typing import Any, Callable, List
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps, partial

from userge import logging, Config

_WORKERS = Config.WORKERS
_THREAD_POOL: ThreadPoolExecutor
_ASYNC_QUEUE = asyncio.Queue()
_TASKS: List[asyncio.Task] = []
_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  ||||  %s  ||||  !>>>"


def submit_task(task: asyncio.coroutines.CoroWrapper) -> None:
    """ submit task to task pool """
    _ASYNC_QUEUE.put_nowait(task)


def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """ submit thread to thread pool """
    return _THREAD_POOL.submit(func, *args, **kwargs)


def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """ run in a thread """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_THREAD_POOL, partial(func, *args, **kwargs))
    return wrapper


def _start():
    global _THREAD_POOL  # pylint: disable=global-statement
    _THREAD_POOL = ThreadPoolExecutor(_WORKERS)

    async def _task_worker():
        while True:
            coro = await _ASYNC_QUEUE.get()
            if coro is None:
                break
            await coro
    loop = asyncio.get_event_loop()
    for _ in range(_WORKERS):
        _TASKS.append(loop.create_task(_task_worker()))
    _LOG.info(_LOG_STR, f"Started Pool : {_WORKERS} Workers")


async def _stop():
    _THREAD_POOL.shutdown()
    for _ in range(_WORKERS):
        _ASYNC_QUEUE.put_nowait(None)
    for task in _TASKS:
        try:
            await asyncio.wait_for(task, timeout=0.3)
        except asyncio.TimeoutError:
            task.cancel()
    _TASKS.clear()
    _LOG.info(_LOG_STR, f"Stopped Pool : {_WORKERS} Workers")
