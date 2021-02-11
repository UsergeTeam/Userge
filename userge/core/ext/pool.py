# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['submit_thread', 'run_in_thread']

import asyncio
from typing import Any, Callable
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps, partial

from motor.frameworks.asyncio import _EXECUTOR  # pylint: disable=protected-access

from userge import logging

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  ||||  %s  ||||  !>>>"


def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """ submit thread to thread pool """
    return _EXECUTOR.submit(func, *args, **kwargs)


def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """ run in a thread """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_EXECUTOR, partial(func, *args, **kwargs))
    return wrapper


def _get() -> ThreadPoolExecutor:
    return _EXECUTOR


def _stop():
    _EXECUTOR.shutdown()
    # pylint: disable=protected-access
    _LOG.info(_LOG_STR, f"Stopped Pool : {_EXECUTOR._max_workers} Workers")


# pylint: disable=protected-access
_LOG.info(_LOG_STR, f"Started Pool : {_EXECUTOR._max_workers} Workers")
