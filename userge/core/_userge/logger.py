# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram import Message as RawMessage
from userge.utils import Config, logging
from .base import BaseCLogger, BaseClient, BaseMessage

LOG = logging.getLogger(__name__)
LOG_STR = "<<<!  (((((  ___{}___  )))))  !>>>"


class CLogger(BaseCLogger):
    """
    Channel logger for Userge.
    """

    def __init__(self, client: BaseClient, name: str) -> None:
        self.__client = client
        self.__string = "**logger** : #" + name.split('.')[-1].upper() + "\n\n{}"

    async def log(self, text: str) -> None:
        """
        send text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.
        Returns:
            None
        """

        LOG.debug(
            LOG_STR.format(f"logging text : {text} to channel : {Config.LOG_CHANNEL_ID}"))

        if Config.LOG_CHANNEL_ID:
            await self.__client.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                             text=self.__string.format(text))

    async def fwd_msg(self,
                      message: BaseMessage,
                      as_copy: bool = True,
                      remove_caption: bool = False) -> None:
        """
        forward message to log channel.

        Parameters:
            message (`pyrogram.Message`):
                pass pyrogram.Message object which want to forward.
            as_copy (`bool`, *optional*):
                Pass True to forward messages without the forward header (i.e.: send a copy of the message content so
                that it appears as originally sent by you).
                Defaults to True.
            remove_caption (`bool`, *optional*):
                If set to True and *as_copy* is enabled as well, media captions are not preserved when copying the
                message. Has no effect if *as_copy* is not enabled.
                Defaults to False.
        Returns:
            None
        """

        LOG.debug(
            LOG_STR.format(f"logging msg : {message} to channel : {Config.LOG_CHANNEL_ID}"))

        if Config.LOG_CHANNEL_ID and isinstance(message, RawMessage):
            await self.__client.forward_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                 from_chat_id=message.chat.id,
                                                 message_ids=(message.message_id),
                                                 as_copy=as_copy,
                                                 remove_caption=remove_caption)
