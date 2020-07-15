# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['submit_thread', 'submit_process',
           'map_threads', 'map_processes',
           'run_in_thread', 'run_in_process']

import asyncio
from typing import Any, Callable, Optional, Union, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from functools import wraps, partial

_THREAD_POOL = ThreadPoolExecutor(4)
_PROCESS_POOL = ProcessPoolExecutor(4)


def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """ submit thread to thread pool """
    return _THREAD_POOL.submit(func, *args, **kwargs)


def submit_process(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """ submit process to process pool """
    return _PROCESS_POOL.submit(func, *args, **kwargs)


def map_threads(func: Callable[[Any], Any],
                *iterables: Iterable[Any],
                timeout: Optional[Union[int, float]] = None,
                chunksize: int = 1) -> Iterator[Future]:
    """ map threads to thread pool """
    return _THREAD_POOL.map(func, *iterables, timeout=timeout, chunksize=chunksize)


def map_processes(func: Callable[[Any], Any],
                  *iterables: Iterable[Any],
                  timeout: Optional[Union[int, float]] = None,
                  chunksize: int = 1) -> Iterator[Future]:
    """ map processes to process pool """
    return _PROCESS_POOL.map(func, *iterables, timeout=timeout, chunksize=chunksize)


def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """ run in a thread """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_THREAD_POOL, partial(func, *args, **kwargs))
    return wrapper


async def run_in_process(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Any:
    """ run in a process """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_PROCESS_POOL, partial(func, *args, **kwargs))
