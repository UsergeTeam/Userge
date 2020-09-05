# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['RawClient']

import time
from typing import Optional

from pyrogram import Client

import userge  # pylint: disable=unused-import


class RawClient(Client):
    """ userge raw client """
    DUAL_MODE = False
    LAST_OUTGOING_TIME = time.time()

    def __init__(self, bot: Optional['userge.core.client._UsergeBot'] = None, **kwargs) -> None:
        self._bot = bot
        super().__init__(**kwargs)
        self._channel = userge.core.types.new.ChannelLogger(self, "CORE")
        userge.core.types.new.Conversation.init(self)
