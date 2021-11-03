""" setup antispam """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved

import json
import asyncio
from typing import Union

from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired, UserAdminInvalid, ChannelInvalid, PeerIdInvalid)

import aiohttp
import spamwatch
from spamwatch.types import Ban
from UsergeAntiSpamApi import Client

from userge import userge, Message, Config, get_collection, filters, pool

SAVED_SETTINGS = get_collection("CONFIGS")
GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


async def _init() -> None:
    s_o = await SAVED_SETTINGS.find_one({'_id': 'ANTISPAM_ENABLED'})
    if s_o:
        Config.ANTISPAM_SENTRY = s_o['data']


@userge.on_cmd("antispam", about={
    'header': "enable / disable antispam",
    'description': "Toggle API Auto Bans"}, allow_channels=False)
async def antispam_(message: Message):
    """ enable / disable antispam """
    if Config.ANTISPAM_SENTRY:
        Config.ANTISPAM_SENTRY = False
        await message.edit("`antispam disabled !`", del_in=3)
    else:
        Config.ANTISPAM_SENTRY = True
        await message.edit("`antispam enabled !`", del_in=3)
    await SAVED_SETTINGS.update_one(
        {'_id': 'ANTISPAM_ENABLED'}, {"$set": {'data': Config.ANTISPAM_SENTRY}}, upsert=True)


@userge.on_filters(filters.group & filters.new_chat_members, group=1, check_restrict_perm=True)
async def gban_at_entry(message: Message):
    """ handle gbans """
    chat_id = message.chat.id
    warned = False
    for user in message.new_chat_members:
        user_id = user.id
        first_name = user.first_name
        if await WHITELIST.find_one({'user_id': user_id}):
            continue
        gbanned = await GBAN_USER_BASE.find_one({'user_id': user_id})
        if gbanned:
            if 'chat_ids' in gbanned:
                chat_ids = gbanned['chat_ids']
                chat_ids.append(chat_id)
            else:
                chat_ids = [chat_id]
            try:
                await asyncio.gather(
                    message.client.kick_chat_member(chat_id, user_id),
                    message.reply(
                        r"\\**#Userge_Antispam**//"
                        "\n\nGlobally Banned User Detected in this Chat.\n\n"
                        f"**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** `{gbanned['reason']}`\n\n"
                        "**Quick Action:** Banned", del_in=10),
                    CHANNEL.log(
                        r"\\**#Antispam_Log**//"
                        "\n\n**GBanned User $SPOTTED**\n"
                        f"**User:** [{first_name}](tg://user?id={user_id})\n"
                        f"**ID:** `{user_id}`\n**Reason:** {gbanned['reason']}\n**Quick Action:** "
                        f"Banned in {message.chat.title}"),
                    GBAN_USER_BASE.update_one(
                        {'user_id': user_id, 'firstname': first_name},
                        {"$set": {'chat_ids': chat_ids}}, upsert=True)
                )
            except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid, PeerIdInvalid):
                pass
        elif Config.ANTISPAM_SENTRY:
            res = await getData(f'https://api.cas.chat/check?user_id={user_id}')
            if res['ok']:
                reason = ' | '.join(
                    res['result']['messages']) if 'result' in res else None
                try:
                    await asyncio.gather(
                        message.client.kick_chat_member(chat_id, user_id),
                        message.reply(
                            r"\\**#Userge_Antispam**//"
                            "\n\nGlobally Banned User Detected in this Chat.\n\n"
                            "**$SENTRY CAS Federation Ban**\n"
                            f"**User:** [{first_name}](tg://user?id={user_id})\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n\n"
                            "**Quick Action:** Banned", del_in=10),
                        CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            "\n\n**GBanned User $SPOTTED**\n"
                            "**$SENRTY #CAS BAN**"
                            f"\n**User:** [{first_name}](tg://user?id={user_id})\n"
                            f"**ID:** `{user_id}`\n**Reason:** `{reason}`\n**Quick Action:**"
                            f" Banned in {message.chat.title}\n\n$AUTOBAN #id{user_id}")
                    )
                except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid, PeerIdInvalid):
                    pass
                continue
            if Config.USERGE_ANTISPAM_API:
                try:
                    ban = await _get_userge_antispam_data(user_id)
                except Exception as err:
                    if not warned:
                        LOG.error(err)
                        await CHANNEL.log(err)
                        warned = True
                else:
                    if ban:
                        try:
                            await asyncio.gather(
                                message.client.kick_chat_member(chat_id, user_id),
                                message.reply(
                                    r"\\**#Userge_Antispam**//"
                                    "\n\nGlobally Banned User Detected in this Chat.\n\n"
                                    "**$SENTRY Userge AntiSpam API Ban**\n"
                                    f"**User:** [{first_name}](tg://user?id={user_id})\n"
                                    f"**ID:** `{user_id}`\n**Reason:** `{ban.reason}`\n\n"
                                    "**Quick Action:** Banned", del_in=10),
                                CHANNEL.log(
                                    r"\\**#Antispam_Log**//"
                                    "\n\n**GBanned User $SPOTTED**\n"
                                    "**$SENRTY #USERGE_ANTISPAM_API BAN**"
                                    f"\n**User:** [{first_name}](tg://user?id={user_id})\n"
                                    f"**ID:** `{user_id}`\n**Reason:** `{ban.reason}`\n"
                                    f"**Quick Action:** Banned in {message.chat.title}\n\n"
                                    f"$AUTOBAN #id{user_id}")
                            )
                        except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid, PeerIdInvalid):
                            pass
                        continue
            if Config.SPAM_WATCH_API:
                intruder = await _get_spamwatch_data(user_id)
                if intruder:
                    try:
                        await asyncio.gather(
                            message.client.kick_chat_member(chat_id, user_id),
                            message.reply(
                                r"\\**#Userge_Antispam**//"
                                "\n\nGlobally Banned User Detected in this Chat.\n\n"
                                "**$SENTRY SpamWatch Federation Ban**\n"
                                f"**User:** [{first_name}](tg://user?id={user_id})\n"
                                f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n\n"
                                "**Quick Action:** Banned", del_in=10),
                            CHANNEL.log(
                                r"\\**#Antispam_Log**//"
                                "\n\n**GBanned User $SPOTTED**\n"
                                "**$SENRTY #SPAMWATCH_API BAN**"
                                f"\n**User:** [{first_name}](tg://user?id={user_id})\n"
                                f"**ID:** `{user_id}`\n**Reason:** `{intruder.reason}`\n"
                                f"**Quick Action:** Banned in {message.chat.title}\n\n"
                                f"$AUTOBAN #id{user_id}")
                        )
                    except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid, PeerIdInvalid):
                        pass
    message.continue_propagation()


async def getData(link: str):
    async with aiohttp.ClientSession() as ses, ses.get(link) as resp:
        try:
            return json.loads(await resp.text())
        except json.decoder.JSONDecodeError:
            return dict(ok=False, success=False)


@pool.run_in_thread
def _get_userge_antispam_data(user_id: int):
    return Client(Config.USERGE_ANTISPAM_API).getban(user_id)


@pool.run_in_thread
def _get_spamwatch_data(user_id: int) -> Union[Ban, bool]:
    return spamwatch.Client(Config.SPAM_WATCH_API).get_ban(user_id)
