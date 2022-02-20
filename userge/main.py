# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import StopPropagation
from pyrogram.raw.base import Message
from pyrogram.raw.types import MessageService, MessageActionContactSignUp

from userge import userge


@userge.on_raw_update(-5)
async def _on_raw(_, m: Message, *__) -> None:
    if isinstance(m, MessageService) and isinstance(m.action, MessageActionContactSignUp):
        raise StopPropagation
