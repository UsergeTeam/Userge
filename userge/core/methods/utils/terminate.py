# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Terminate']

from ...ext import RawClient


class Terminate(RawClient):  # pylint: disable=missing-class-docstring
    async def terminate(self) -> None:
        """ terminate userge """
        if not self.no_updates:
            for task in self.dispatcher.handler_worker_tasks:
                task.cancel()
            self.dispatcher.handler_worker_tasks.clear()
        await super().terminate()
