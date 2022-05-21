""" setup antispam """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Optional, Tuple

import aiohttp
import spamwatch
from UsergeAntiSpamApi import Client
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired, UserAdminInvalid, PeerIdInvalid)
from pyrogram.types import User, Chat

from userge import userge, Message, get_collection, filters, pool
from .. import antispam
from ..gban import is_whitelist

SAVED_SETTINGS = get_collection("CONFIGS")
GBAN_USER_BASE = get_collection("GBAN_USER")

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)

HANDLER = None
_ID = {'_id': 'ANTISPAM_ENABLED'}


@userge.on_start
async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one(_ID)
    if s_o:
        antispam.Dynamic.ANTISPAM_SENTRY = s_o['data']
    await _re_init_handler()


class Handler(ABC):
    @abstractmethod
    def set_next(self, handler: 'Handler') -> 'Handler':
        pass

    @abstractmethod
    async def handle(self, message: Message, user: User) -> None:
        pass


class AbstractHandler(Handler, ABC):
    def __init__(self, name: Optional[str] = None) -> None:
        self._name = name
        self._next: Optional[Handler] = None

    def set_next(self, handler: Handler) -> Handler:
        self._next = handler
        return handler

    async def handle(self, message: Message, user: User) -> None:
        propagate = await self._handle(message, user)
        if propagate and self._next:
            await self._next.handle(message, user)

    async def _handle(self, message: Message, user: User) -> bool:
        user_id = user.id
        data = await self.get_data(user_id)
        if not data:
            return True

        chat = message.chat
        try:
            await message.client.ban_chat_member(chat.id, user_id)
        except PeerIdInvalid:
            return False

        await self.on_handle(chat, user, data)
        asyncio.create_task(self._do_handle(message, user, data))
        return False

    async def _do_handle(self, message: Message, user: User, data) -> None:
        reason = self.get_reason(data)
        msg, log = _get_msg_and_log(message.chat, user, reason or 'None', self._name)
        task = asyncio.create_task(message.reply(msg, del_in=10))
        await CHANNEL.log(log)
        await task

    @abstractmethod
    async def get_data(self, user_id: int):
        """ return the object if user is banned """

    @abstractmethod
    def get_reason(self, data) -> Optional[str]:
        """ return the ban reason """

    async def on_handle(self, chat: Chat, user: User, data) -> None:
        pass


def _get_msg_and_log(chat: Chat, user: User, reason: str, fed: Optional[str]) -> Tuple[str, str]:
    user_id = user.id
    first_name = user.first_name

    others = f"**$SENTRY {fed} Federation Ban**\n" if fed else ""
    others += (
        f"**User:** [{first_name}](tg://user?id={user_id})\n"
        f"**ID:** `{user_id}`\n**Reason:** `:reason:`\n\n"
        "**Quick Action:** Banned"
    )

    msg = (
        r"\\**#Userge_Antispam**//"
        "\n\nGlobally Banned User Detected in this Chat.\n\n"
        f"{others.replace(':reason:', reason[:97] + '...' if len(reason) > 97 else reason)}"
    )

    log = (
        r"\\**#Antispam_Log**//"
        "\n\n**GBanned User $SPOTTED**\n\n"
        f"{others.replace(':reason:', reason)} in {chat.title}"
    )

    return msg, log


class GBanHandler(AbstractHandler):
    async def get_data(self, user_id: int):
        return await GBAN_USER_BASE.find_one({'user_id': user_id})

    def get_reason(self, data) -> Optional[str]:
        return data.get('reason')

    async def on_handle(self, chat: Chat, user: User, data) -> None:
        chat_ids = data.get('chat_ids', [])
        chat_ids.append(chat.id)
        await GBAN_USER_BASE.update_one({'user_id': user.id, 'firstname': user.first_name},
                                        {"$set": {'chat_ids': chat_ids}}, upsert=True)


class CASHandler(AbstractHandler):
    def __init__(self) -> None:
        self._url = "https://api.cas.chat/check?user_id={user_id}"
        super().__init__("CAS")

    async def get_data(self, user_id: int):
        url = self._url.format(user_id=user_id)
        async with aiohttp.ClientSession() as ses, ses.get(url) as resp:
            try:
                data = json.loads(await resp.text())
            except json.decoder.JSONDecodeError:
                data = dict(ok=False)
            if data.get('ok'):
                return data

    def get_reason(self, data) -> Optional[str]:
        return ' | '.join(data['result']['messages']) if 'result' in data else None


class UsergeAntiSpamHandler(AbstractHandler):
    def __init__(self) -> None:
        self._client = Client(antispam.USERGE_ANTISPAM_API)
        super().__init__("UsergeAntiSpamAPI")

    async def get_data(self, user_id: int):
        try:
            return await pool.run_in_thread(self._client.getban)(user_id)
        except Exception as err:
            LOG.error(err)

    def get_reason(self, data) -> Optional[str]:
        return data.reason


class SpamWatchHandler(AbstractHandler):
    def __init__(self) -> None:
        self._client = spamwatch.Client(antispam.SPAM_WATCH_API)
        super().__init__("SpamWatch")

    async def get_data(self, user_id: int):
        try:
            return await pool.run_in_thread(self._client.get_ban)(user_id)
        except Exception as err:
            LOG.error(err)

    def get_reason(self, data) -> Optional[str]:
        return data.reason


@pool.run_in_thread
def _re_init_handler():
    global HANDLER  # pylint: disable=global-statement
    handler = GBanHandler()
    if antispam.Dynamic.ANTISPAM_SENTRY:
        tmp = handler.set_next(CASHandler())
        if antispam.USERGE_ANTISPAM_API:
            tmp = tmp.set_next(UsergeAntiSpamHandler())
        if antispam.SPAM_WATCH_API:
            tmp.set_next(SpamWatchHandler())
    HANDLER = handler


@userge.on_cmd("antispam", about={
    'header': "enable / disable antispam",
    'description': "Toggle API Auto Bans"}, allow_channels=False)
async def antispam_(message: Message):
    """ enable / disable antispam """
    antispam.Dynamic.ANTISPAM_SENTRY = not antispam.Dynamic.ANTISPAM_SENTRY
    text = f"`antispam {'enabled' if antispam.Dynamic.ANTISPAM_SENTRY else 'disabled'} !`"
    await message.edit(text, del_in=3)
    await _re_init_handler()
    await SAVED_SETTINGS.update_one(
        _ID, {"$set": {'data': antispam.Dynamic.ANTISPAM_SENTRY}}, upsert=True
    )


@userge.on_filters(filters.group & filters.new_chat_members, group=1,
                   propagate=True, check_restrict_perm=True)
async def gban_at_entry(message: Message):
    """ handle gbans """
    if isinstance(HANDLER, Handler):
        try:
            for user in message.new_chat_members:
                if await is_whitelist(user.id):
                    continue
                await HANDLER.handle(message, user)
        except (ChatAdminRequired, UserAdminInvalid):
            pass
