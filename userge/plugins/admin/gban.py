""" setup gban """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved

import asyncio

from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired, UserAdminInvalid, ChannelInvalid)

from userge import userge, Message, Config, get_collection

GBAN_USER_BASE = get_collection("GBAN_USER")
WHITELIST = get_collection("WHITELIST_USER")
CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


@userge.on_cmd("gban", about={
    'header': "Globally Ban A User",
    'description': "Adds User to your GBan List. "
                   "Bans a Globally Banned user if they join or message. "
                   "[NOTE: Works only in groups where you are admin.]",
    'examples': "{tr}gban [userid | reply] [reason for gban] (mandatory)"},
    allow_channels=False, allow_bots=False)
async def gban_user(message: Message):
    """ ban a user globally """
    await message.edit("`GBanning...`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            "`no valid user_id or message specified,`"
            "`don't do .help gban for more info. "
            "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠", del_in=0)
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    if not reason:
        await message.edit(
            f"**#Aborted**\n\n**Gbanning** of [{firstname}](tg://user?id={user_id}) "
            "Aborted coz No reason of gban provided by banner", del_in=5)
        return
    user_id = get_mem['id']
    if user_id == (await message.client.get_me()).id:
        await message.edit(r"LoL. Why would I GBan myself ¯\(°_o)/¯")
        return
    if user_id in Config.SUDO_USERS:
        await message.edit(
            "That user is in my Sudo List, Hence I can't ban him.\n\n"
            "**Tip:** Remove them from Sudo List and try again. (¬_¬)", del_in=5)
        return
    found = await GBAN_USER_BASE.find_one({'user_id': user_id})
    if found:
        await message.edit(
            "**#Already_GBanned**\n\nUser Already Exists in My Gban List.\n"
            f"**Reason For GBan:** `{found['reason']}`", del_in=5)
        return
    await message.edit(r"\\**#GBanned_User**//"
                       f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
                       f"**User ID:** `{user_id}`\n**Reason:** `{reason}`")
    # TODO: can we add something like "GBanned by {any_sudo_user_fname}"
    if message.client.is_bot:
        chats = [message.chat]
    else:
        chats = await message.client.get_common_chats(user_id)
    gbanned_chats = []
    for chat in chats:
        try:
            await chat.kick_member(user_id)
            gbanned_chats.append(chat.id)
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n"
                f"**Reason:** `{reason}`\n\n$GBAN #id{user_id}")
        except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
            pass
    await GBAN_USER_BASE.insert_one({'firstname': firstname,
                                     'user_id': user_id,
                                     'reason': reason,
                                     'chat_ids': gbanned_chats})
    if message.reply_to_message:
        await CHANNEL.fwd_msg(message.reply_to_message)
        await CHANNEL.log(f'$GBAN #prid{user_id} ⬆️')
    LOG.info("G-Banned %s", str(user_id))


@userge.on_cmd("ungban", about={
    'header': "Globally Unban an User",
    'description': "Removes an user from your Gban List",
    'examples': "{tr}ungban [userid | reply]"},
    allow_channels=False, allow_bots=False)
async def ungban_user(message: Message):
    """ unban a user globally """
    await message.edit("`UnGBanning...`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']
    found = await GBAN_USER_BASE.find_one({'user_id': user_id})
    if not found:
        await message.err("User Not Found in My Gban List")
        return
    if 'chat_ids' in found:
        for chat_id in found['chat_ids']:
            try:
                await userge.unban_chat_member(chat_id, user_id)
                await CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                    f"**User ID:** `{user_id}`\n\n"
                    f"$UNGBAN #id{user_id}")
            except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
                pass
    await message.edit(r"\\**#UnGbanned_User**//"
                       f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
                       f"**User ID:** `{user_id}`")
    await GBAN_USER_BASE.delete_one({'firstname': firstname, 'user_id': user_id})
    LOG.info("UnGbanned %s", str(user_id))


@userge.on_cmd("glist", about={
    'header': "Get a List of Gbanned Users",
    'description': "Get Up-to-date list of users Gbanned by you.",
    'examples': "Lol. Just type {tr}glist"},
    allow_channels=False)
async def list_gbanned(message: Message):
    """ vies gbanned users """
    msg = ''
    async for c in GBAN_USER_BASE.find():
        msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> "
                + str(c['user_id']) + " is **GBanned for** : " + str(c.get('reason')) + "\n\n")
    await message.edit_or_send_as_file(
        f"**--Globally Banned Users List--**\n\n{msg}" if msg else "`glist empty!`")


@userge.on_cmd("whitelist", about={
    'header': "Whitelist a User",
    'description': "Use whitelist to add users to bypass API Bans",
    'usage': "{tr}whitelist [userid | reply to user]",
    'examples': "{tr}whitelist 5231147869"},
    allow_channels=False, allow_bots=False)
async def whitelist(message: Message):
    """ add user to whitelist """
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']
    found = await WHITELIST.find_one({'user_id': user_id})
    if found:
        await message.err("User Already in My WhiteList")
        return
    await asyncio.gather(
        WHITELIST.insert_one({'firstname': firstname, 'user_id': user_id}),
        message.edit(
            r"\\**#Whitelisted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`"),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$WHITELISTED #id{user_id}")
    )
    LOG.info("WhiteListed %s", str(user_id))


@userge.on_cmd("rmwhite", about={
    'header': "Removes a User from Whitelist",
    'description': "Use it to remove users from WhiteList",
    'useage': "{tr}rmwhite [userid | reply to user]",
    'examples': "{tr}rmwhite 5231147869"},
    allow_channels=False, allow_bots=False)
async def rmwhitelist(message: Message):
    """ remove a user from whitelist """
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.err("user-id not found")
        return
    get_mem = await message.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']
    found = await WHITELIST.find_one({'user_id': user_id})
    if not found:
        await message.err("User Not Found in My WhiteList")
        return
    await asyncio.gather(
        WHITELIST.delete_one({'firstname': firstname, 'user_id': user_id}),
        message.edit(
            r"\\**#Removed_Whitelisted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`"),
        CHANNEL.log(
            r"\\**#Antispam_Log**//"
            f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n"
            f"**Chat:** {message.chat.title}\n"
            f"**Chat ID:** `{message.chat.id}`\n\n$RMWHITELISTED #id{user_id}")
    )
    LOG.info("WhiteListed %s", str(user_id))


@userge.on_cmd("listwhite", about={
    'header': "Get a List of Whitelisted Users",
    'description': "Get Up-to-date list of users WhiteListed by you.",
    'examples': "Lol. Just type {tr}listwhite"},
    allow_channels=False)
async def list_white(message: Message):
    """ list whitelist """
    msg = ''
    async for c in WHITELIST.find():
        msg += ("**User** : " + str(c['firstname']) + "-> with **User ID** -> " +
                str(c['user_id']) + "\n\n")
    await message.edit_or_send_as_file(
        f"**--Whitelisted Users List--**\n\n{msg}" if msg else "`whitelist empty!`")
