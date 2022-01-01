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

import os
import sys
import signal

import psutil

from userge import logging
from ...ext import RawClient

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  #####  %s  #####  !>>>"


class Restart(RawClient):  # pylint: disable=missing-class-docstring
    async def restart(self, update_req: bool = False,  # pylint: disable=arguments-differ
                      hard: bool = False) -> None:
        """ Restart the AbstractUserge """
        _LOG.info(_LOG_STR, "Restarting Userge")
        await self.stop()
        if update_req:
            _LOG.info(_LOG_STR, "Installing Requirements...")
            os.system(  # nosec
                "pip3 install -U pip && pip3 install -r requirements.txt")
            _LOG.info(_LOG_STR, "Requirements Installed !")
        if hard:
            os.kill(os.getpid(), signal.SIGUSR1)
        else:
            try:
                c_p = psutil.Process(os.getpid())
                for handler in c_p.open_files() + c_p.connections():
                    os.close(handler.fd)
            except Exception as c_e:  # pylint: disable=broad-except
                print(_LOG_STR % c_e)
            os.execl(sys.executable, sys.executable, '-m', 'userge')  # nosec
            sys.exit()
