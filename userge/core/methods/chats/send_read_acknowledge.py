# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['SendReadAcknowledge']

from typing import List, Optional, Union

from pyrogram.raw import functions

from ...ext import RawClient, RawMessage


class SendReadAcknowledge(RawClient):  # pylint: disable=missing-class-docstring
    async def send_read_acknowledge(self,
                                    chat_id: Union[int, str],
                                    message: Union[List[RawMessage],
                                                   Optional[RawMessage]] = None,
                                    *, max_id: Optional[int] = None,
                                    clear_mentions: bool = False) -> bool:
        """\nMarks messages as read and optionally clears mentions.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            message (``list`` | :obj: `Message`, *optional*):
                Either a list of messages or a single message.

            max_id (``int``, *optional*):
                Until which message should the read acknowledge be sent for.
                This has priority over the ``message`` parameter.

            clear_mentions (``bool``, *optional*):
                Whether the mention badge should be cleared (so that
                there are no more mentions) or not for the given entity.
                If no message is provided, this will be the only action
                taken.
                defaults to False.

        Returns:
            On success, True is returned.
        """
        if max_id is None:
            if message:
                if isinstance(message, list):
                    max_id = max(msg.id for msg in message)
                else:
                    max_id = message.id
            else:
                max_id = 0
        if clear_mentions:
            await self.invoke(
                functions.messages.ReadMentions(
                    peer=await self.resolve_peer(chat_id)))
            if max_id is None:
                return True
        if max_id is not None:
            return bool(await self.read_chat_history(chat_id=chat_id, max_id=max_id))
        return False
