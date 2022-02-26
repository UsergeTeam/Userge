# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Restart']

from loader.userge.api import restart
from userge import logging
from ...ext import RawClient

_LOG = logging.getLogger(__name__)


class Restart(RawClient):  # pylint: disable=missing-class-docstring
    @staticmethod
    async def restart(hard: bool = False, **_) -> None:
        """ Restart the Userge """
        _LOG.info(f"Restarting Userge [{'HARD' if hard else 'SOFT'}]")
        restart(hard)
