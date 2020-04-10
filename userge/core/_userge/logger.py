from userge.utils import Config
from .base import Base
from .message import Message


class CLogger:
    """
    Channel logger for Userge.
    """

    def __init__(self, client: Base, name: str) -> None:
        self.__client = client
        self.__string = "**logger** : `" + name + "`\n\n{}"

    async def log(self, text: str) -> None:
        """
        send text message to log channel.

        Parameters:
            text (``str``):
                Text of the message to be sent.
        Returns:
            None
        """
        if Config.LOG_CHANNEL_ID:
            await self.__client.send_message(chat_id=Config.LOG_CHANNEL_ID,
                                             text=self.__string.format(text))

    async def fwd_msg(self,
                      message: Message,
                      as_copy=False,
                      remove_caption=False) -> None:
        """
        forward message to log channel.

        Parameters:
            message (`pyrogram.Message`):
                pass pyrogram.Message object which want to forward.
            as_copy (`bool`, *optional*):
                Pass True to forward messages without the forward header (i.e.: send a copy of the message content so
                that it appears as originally sent by you).
                Defaults to False.
            remove_caption (`bool`, *optional*):
                If set to True and *as_copy* is enabled as well, media captions are not preserved when copying the
                message. Has no effect if *as_copy* is not enabled.
                Defaults to False.
        Returns:
            None
        """

        if Config.LOG_CHANNEL_ID:
            await self.__client.forward_messages(chat_id=Config.LOG_CHANNEL_ID,
                                                 from_chat_id=message.chat.id,
                                                 message_ids=(message.message_id),
                                                 as_copy=as_copy,
                                                 remove_caption=remove_caption)
