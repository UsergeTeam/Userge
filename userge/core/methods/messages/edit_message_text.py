# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['EditMessageText']

import inspect
import asyncio
from typing import Optional, Union, List

from pyrogram.types import InlineKeyboardMarkup, MessageEntity

from userge import Config
from userge.utils import secure_text
from ...ext import RawClient
from ... import types


class EditMessageText(RawClient):  # pylint: disable=missing-class-docstring
    async def edit_message_text(self,  # pylint: disable=arguments-differ
                                chat_id: Union[int, str],
                                message_id: int,
                                text: str,
                                del_in: int = -1,
                                log: Union[bool, str] = False,
                                parse_mode: Union[str, object] = object,
                                entities: List[MessageEntity] = None,
                                disable_web_page_preview: Optional[bool] = None,
                                reply_markup: InlineKeyboardMarkup = None
                                ) -> Union['types.bound.Message', bool]:
        """\nExample:
                message.edit_text("hello")

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages)
                you can simply use "me" or "self".
                For a contact that exists in your Telegram address book
                you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in chat_id.

            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text,
                which can be specified instead of *parse_mode*.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited
            :obj:`Message` or True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if text and chat_id not in Config.AUTH_CHATS:
            text = secure_text(str(text))
        msg = await super().edit_message_text(chat_id=chat_id,
                                              message_id=message_id,
                                              text=text,
                                              parse_mode=parse_mode,
                                              entities=entities,
                                              disable_web_page_preview=disable_web_page_preview,
                                              reply_markup=reply_markup)
        module = inspect.currentframe().f_back.f_globals['__name__']
        if log:
            await self._channel.fwd_msg(msg, module if isinstance(log, bool) else log)
        del_in = del_in or Config.MSG_DELETE_TIMEOUT
        if del_in > 0:
            await asyncio.sleep(del_in)
            return bool(await msg.delete())
        return types.bound.Message.parse(self, msg, module=module)
