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

from typing import Optional

import nest_asyncio
from pyrogram import Client

from .. import types, client  # pylint: disable=unused-import


class RawClient(Client):
    """ userge raw client """
    DUAL_MODE = False

    def __init__(self, bot: Optional['client._UsergeBot'] = None, **kwargs) -> None:
        self._bot = bot
        super().__init__(**kwargs)
        self._channel = types.new.ChannelLogger(self, "CORE")
        types.new.Conversation.init(self)
        nest_asyncio.apply()
