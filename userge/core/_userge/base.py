# Copyright (C) 2020 by UsergeTeam@Telegram, < https://t.me/theUserge >.
#
# This file is part of < https://github.com/uaudith/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram import Client, Message


class BaseMessage(Message):
    """
    Base Class for Message.
    """

    @property
    def process_is_canceled(self) -> bool:
        pass


class BaseCLogger:
    """
    Base Class for CLogger.
    """

    async def fwd_msg(self,
                      message: BaseMessage,
                      as_copy: bool = False,
                      remove_caption: bool = False) -> None:
        pass


class BaseClient(Client):
    """
    Base Class for Client.
    """

    def getCLogger(self, name: str) -> BaseCLogger:
        pass
