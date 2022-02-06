""" Anti-Flood Module to control Spam """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
import asyncio

from pyrogram import filters
from pyrogram.types import ChatPermissions

from userge import userge, Message, get_collection

ANTIFLOOD_DATA = {}
ADMINS = {}
FLOOD_CACHE = {}

ANTI_FLOOD = get_collection("ANTIFLOOD")

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    async for data in ANTI_FLOOD.find():
        ANTIFLOOD_DATA[data["chat_id"]] = {
            "data": data["data"],
            "limit": data["limit"],
            "mode": "Ban"
        }


async def cache_admins(msg):
    au_ids = []
    async for admins in msg.chat.iter_members(filter="administrators"):
        au_ids.append(admins.user.id)
    ADMINS[msg.chat.id] = au_ids


@userge.on_cmd("setflood", about={
    'header': "Set Anti-Flood limit to take Action\n"
              "Pass <on/off> to turn Off and On.",
    'usage': "{tr}setflood 5\n"
             "{tr}setflood on (for ON)\n{tr}setflood off (for OFF)"}, allow_private=False)
async def set_flood(msg: Message):
    """ Set flood on/off and flood limit """
    args = msg.input_str
    if not args:
        await msg.err("Input not found!")
        return
    if 'on' in args.lower():
        if msg.chat.id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[msg.chat.id].get("data") == "on":
            return await msg.edit("Antiflood Already enabled for this chat.", del_in=5)
        chat_limit = 5
        chat_mode = "Ban"
        if ANTIFLOOD_DATA.get(msg.chat.id):
            chat_limit = ANTIFLOOD_DATA[msg.chat.id].get("limit")
            chat_mode = ANTIFLOOD_DATA[msg.chat.id].get("mode")
        ANTIFLOOD_DATA[msg.chat.id] = {
            "data": "on",
            "limit": chat_limit,
            "mode": chat_mode
        }
        await ANTI_FLOOD.update_one(
            {'chat_id': msg.chat.id},
            {"$set": {
                'data': 'on',
                'limit': chat_limit,
                'mode': chat_mode
            }},
            upsert=True
        )
        await msg.edit("`Anti-Flood is Enabled Successfully...`", log=__name__, del_in=5)
    elif 'off' in args.lower():
        if msg.chat.id not in ANTIFLOOD_DATA or (
            msg.chat.id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
        ):
            return await msg.edit("Antiflood Already Disabled for this chat.", del_in=5)
        ANTIFLOOD_DATA[msg.chat.id]["data"] = "off"
        await ANTI_FLOOD.update_one(
            {'chat_id': msg.chat.id}, {"$set": {'data': 'off'}}, upsert=True)
        await msg.edit("`Anti-Flood is Disabled Successfully...`", log=__name__, del_in=5)
    elif args.isnumeric():
        if msg.chat.id not in ANTIFLOOD_DATA or (
            msg.chat.id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
        ):
            return await msg.edit("First turn ON ANTIFLOOD then set Limit.", del_in=5)
        input_ = int(args)
        if input_ < 3:
            await msg.err("Can't set Antiflood Limit less then 3")
            return
        ANTIFLOOD_DATA[msg.chat.id]["limit"] = input_
        await ANTI_FLOOD.update_one(
            {'chat_id': msg.chat.id}, {"$set": {'limit': input_}}, upsert=True)
        await msg.edit(
            f"`Anti-Flood  limit is Successfully Updated for {input_}.`",
            log=__name__, del_in=5
        )
    else:
        await msg.err("Invalid argument!")


@userge.on_cmd("setmode", about={
    'header': "Set Anti-Flood Mode",
    'description': "When User Reached Limit of Flooding "
                   "He will Got Ban/Kick/Mute By Group Admins",
    'usage': "{tr}setmode Ban\n{tr}setmode Kick\n{tr}setmode Mute"}, allow_private=False)
async def set_mode(msg: Message):
    """ Set flood mode to take action """
    mode = msg.input_str
    if not mode:
        await msg.err("Input not found!")
        return
    if msg.chat.id not in ANTIFLOOD_DATA or (
        msg.chat.id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[msg.chat.id].get("data") == "off"
    ):
        return await msg.edit("First turn ON ANTIFLOOD then set Mode.", del_in=5)
    if mode.lower() in ('ban', 'kick', 'mute'):
        ANTIFLOOD_DATA[msg.chat.id]["mode"] = mode.lower()
        await ANTI_FLOOD.update_one(
            {'chat_id': msg.chat.id}, {"$set": {'mode': mode.lower()}}, upsert=True)
        await msg.edit(
            f"`Anti-Flood Mode is Successfully Updated to {mode.title()}`",
            log=__name__, del_in=5
        )
    else:
        await msg.err("Invalid argument!")


@userge.on_cmd("vflood", about={
    'header': "View Current Anti Flood Settings",
    'usage': "{tr}vflood"}, allow_private=False)
async def view_flood_settings(msg: Message):
    """ view Current Flood Settings """
    chat_data = ANTIFLOOD_DATA.get(msg.chat.id)
    if not chat_data or (chat_data and chat_data.get("data") == "off"):
        return await msg.edit("`Anti-Flood Disabled in this chat.`")
    limit = chat_data["limit"]
    mode = chat_data["mode"]
    await msg.edit(
        f"**Anti-Flood in {msg.chat.title}**\n"
        "\t\t**Enabled:** `True`\n"
        f"\t\t**Limit:** `{limit}`\n"
        f"\t\t**Mode:** `{mode}`\n"
    )


@userge.on_filters(
    filters.group & filters.incoming & ~filters.edited, group=3, check_restrict_perm=True
)
async def anti_flood_handler(msg: Message):
    """ Filtering msgs for Handling Flooding """

    if not msg.from_user:
        return

    chat_id = msg.chat.id
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name

    if chat_id not in ANTIFLOOD_DATA or (
        chat_id in ANTIFLOOD_DATA and ANTIFLOOD_DATA[chat_id].get("data") == "off"
    ):
        return

    if not ADMINS.get(msg.chat.id):
        await cache_admins(msg)
    if user_id in ADMINS[chat_id]:
        if chat_id in FLOOD_CACHE:
            del FLOOD_CACHE[chat_id]
        return

    mode = ANTIFLOOD_DATA[msg.chat.id]["mode"]
    limit = ANTIFLOOD_DATA[msg.chat.id]["limit"]

    if check_flood(chat_id, user_id):
        if mode.lower() == 'ban':
            await msg.client.ban_chat_member(
                chat_id, user_id)
            exec_str = "#BANNED"
        elif mode.lower() == 'kick':
            await msg.client.ban_chat_member(
                chat_id, user_id, int(time.time() + 60))
            exec_str = "#KICKED"
        else:
            await msg.client.restrict_chat_member(
                chat_id, user_id, ChatPermissions())
            exec_str = "#MUTED"
        await asyncio.gather(
            msg.reply(
                r"\\**#Userge_AntiFlood**//"
                "\n\nThis User Reached His Limit of Spamming\n\n"
                f"**User:** [{first_name}](tg://user?id={user_id})\n"
                f"**ID:** `{user_id}`\n**Limit:** `{limit}`\n\n"
                f"**Quick Action:** {exec_str}"),
            CHANNEL.log(
                r"\\**#AntiFlood_Log**//"
                "\n\n**User Anti-Flood Limit reached**\n"
                f"**User:** [{first_name}](tg://user?id={user_id})\n"
                f"**ID:** `{user_id}`\n**Limit:** {limit}\n"
                f"**Quick Action:** {exec_str} in {msg.chat.title}")
        )


def check_flood(chat_id: int, user_id: int):
    if not FLOOD_CACHE.get(chat_id) or FLOOD_CACHE[chat_id]["cur_user"] != user_id:
        FLOOD_CACHE[chat_id] = {
            "cur_user": user_id,
            "count": 1
        }
        return False
    chat_flood = FLOOD_CACHE[chat_id]
    count = chat_flood["count"]

    count += 1
    if count >= ANTIFLOOD_DATA[chat_id]["limit"]:
        del FLOOD_CACHE[chat_id]
        return True
    FLOOD_CACHE[chat_id] = {"cur_user": user_id, "count": count}
    return False
