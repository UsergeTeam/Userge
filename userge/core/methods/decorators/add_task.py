# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['AddTask']

from typing import Callable, Any

from . import RawDecorator


class AddTask(RawDecorator):  # pylint: disable=missing-class-docstring
    def add_task(self, func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """ add tasks """
        self._tasks.append(func)
        return func
