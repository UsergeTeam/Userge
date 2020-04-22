# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram import Message as RawMessage
from userge import logging, Config
from . import client, message

LOG = logging.getLogger(__name__)
LOG_STR = "<<<!  (((((  ___%s___  )))))  !>>>"


class CLogger:
    """
    Channel logger for Userge.
    """

    def __init__(self, client_: 'client.Userge', name: str) -> None:
        self.__client = client_
        self.__string = self.__gen_string(name)

    @staticmethod
    def __gen_string(name: str) -> str:
        return "**logger** : #" + name.split('.')[-1].upper() + "\n\n{}"

    def update(self, name: str) -> None:
        """
        update current logger name.

        Parameters:
            name (``str``):
                New name to logger.
        Returns:
            None
        """

        self.__string = self.__gen_string(name)

    async def log(self, text: str) -> None:
        """
        send text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.
        Returns:
            None
        """

        LOG.debug(LOG_STR, f"logging text : {text} to channel : {Config.LOG_CHANNEL_ID}")

        if Config.LOG_CHANNEL_ID:
            await self.__client.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                             text=self.__string.format(text))

    async def fwd_msg(self,
                      message_: 'message.Message',
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
            LOG_STR, f"forwarding msg : {message_} to channel : {Config.LOG_CHANNEL_ID}")

        if Config.LOG_CHANNEL_ID and isinstance(message_, RawMessage):
            if message_.media:
                await self.log("**Forwarding Message...**")

                await self.__client.forward_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                     from_chat_id=message_.chat.id,
                                                     message_ids=(
                                                         message_.message_id),
                                                     as_copy=as_copy,
                                                     remove_caption=remove_caption)

            else:
                await self.log(message_.text)
