""" setup gmute """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved

import asyncio

from pyrogram.types import ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired, UserAdminInvalid

from userge import userge, Config, Message, get_collection, filters

GMUTE_USER_BASE = get_collection("GMUTE_USER")
CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


@userge.on_cmd("gmute", about={
    'header': "Globally Mute A User",
    'description': "Adds User to your GMute List",
    'examples': "{tr}gmute [userid | reply] [reason for gmute] (mandatory)"},
    allow_channels=False, allow_bots=False)
async def gmute_user(msg: Message):
    """ Mute a user globally """
    await msg.edit("`Globally Muting this User...`")
    user_id, reason = msg.extract_user_and_text
    if not user_id:
        await msg.edit(
            "`no valid user_id or message specified,`"
            "`don't do .help gmute for more info. "
            "Coz no one's gonna help ya`(｡ŏ_ŏ) ⚠")
        return
    get_mem = await msg.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    if not reason:
        await msg.edit(
            f"**#Aborted**\n\n**GMuting** of [{firstname}](tg://user?id={user_id}) "
            "`Aborted coz No reason of GMute provided by User`", del_in=5)
        return
    user_id = get_mem['id']
    if user_id == msg.from_user.id:
        await msg.err(r"LoL. Why would I GMuting myself ¯\(°_o)/¯")
        return
    if user_id in Config.SUDO_USERS:
        await msg.edit(
            "`That user is in my Sudo List, Hence I can't GMute him.`\n\n"
            "**Tip:** `Remove them from Sudo List and try again. (¬_¬)`", del_in=5)
        return
    found = await GMUTE_USER_BASE.find_one({'user_id': user_id})
    if found:
        await msg.edit(
            "**#Already_GMuted**\n\n`This User Already Exists in My GMute List.`\n"
            f"**Reason For GMute:** `{found['reason']}`")
        return
    await asyncio.gather(
        GMUTE_USER_BASE.insert_one(
            {'firstname': firstname, 'user_id': user_id, 'reason': reason}),
        msg.edit(
            r"\\**#GMuted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`\n**Reason:** `{reason}`"))
    chats = [msg.chat] if msg.client.is_bot else await msg.client.get_common_chats(user_id)
    for chat in chats:
        try:
            await chat.restrict_member(user_id, ChatPermissions())
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n"
                f"**Reason:** `{reason}`\n\n$GMUTE #id{user_id}")
        except (ChatAdminRequired, UserAdminInvalid):
            pass
    if msg.reply_to_message:
        await CHANNEL.fwd_msg(msg.reply_to_message)
        await CHANNEL.log(f'$GMUTE #prid{user_id} ⬆️')
    LOG.info("G-Muted %s", str(user_id))


@userge.on_cmd("ungmute", about={
    'header': "Globally Unmute an User",
    'description': "Removes an user from your GMute List",
    'examples': "{tr}ungmute [userid | reply]"},
    allow_channels=False, allow_bots=False)
async def ungmute_user(msg: Message):
    """ unmute a user globally """
    await msg.edit("`UnGMuting this User...`")
    user_id, _ = msg.extract_user_and_text
    if not user_id:
        await msg.err("user-id not found")
        return
    get_mem = await msg.client.get_user_dict(user_id)
    firstname = get_mem['fname']
    user_id = get_mem['id']
    found = await GMUTE_USER_BASE.find_one({'user_id': user_id})
    if not found:
        await msg.err("User Not Found in My GMute List")
        return
    await asyncio.gather(
        GMUTE_USER_BASE.delete_one({'firstname': firstname, 'user_id': user_id}),
        msg.edit(
            r"\\**#UnGMuted_User**//"
            f"\n\n**First Name:** [{firstname}](tg://user?id={user_id})\n"
            f"**User ID:** `{user_id}`"))
    chats = [msg.chat] if msg.client.is_bot else await msg.client.get_common_chats(user_id)
    for chat in chats:
        try:
            await chat.unban_member(user_id)
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** [{firstname}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat:** {chat.title}\n"
                f"**Chat ID:** `{chat.id}`\n\n$UNGMUTED #id{user_id}")
        except (ChatAdminRequired, UserAdminInvalid):
            pass
    LOG.info("UnGMuted %s", str(user_id))


@userge.on_cmd("gmlist", about={
    'header': "Get a List of GMuted Users",
    'description': "Get Up-to-date list of users GMuted by you.",
    'examples': "{tr}gmlist"},
    allow_channels=False)
async def list_gmuted(msg: Message):
    """ views gmuted users """
    users = ''
    async for c in GMUTE_USER_BASE.find():
        users += ("**User** : " + str(c['firstname']))
        users += ("\n**User ID** : " + str(c['user_id']))
        users += ("\n**Reason for GMuted** : " + str(c['reason']) + "\n\n")
    await msg.edit_or_send_as_file(
        f"**--Globally Muted Users List--**\n\n{users}" if users else "`Gmute List is Empty`")


@userge.on_filters(filters.group & filters.new_chat_members, group=1, check_restrict_perm=True)
async def gmute_at_entry(msg: Message):
    """ handle gmute """
    chat_id = msg.chat.id
    for user in msg.new_chat_members:
        user_id = user.id
        first_name = user.first_name
        gmuted = await GMUTE_USER_BASE.find_one({'user_id': user_id})
        if gmuted:
            await asyncio.gather(
                msg.client.restrict_chat_member(chat_id, user_id, ChatPermissions()),
                msg.reply(
                    r"\\**#Userge_Antispam**//"
                    "\n\nGlobally Muted User Detected in this Chat.\n\n"
                    f"**User:** [{first_name}](tg://user?id={user_id})\n"
                    f"**ID:** `{user_id}`\n**Reason:** `{gmuted['reason']}`\n\n"
                    "**Quick Action:** Muted", del_in=10),
                CHANNEL.log(
                    r"\\**#Antispam_Log**//"
                    "\n\n**GMuted User $SPOTTED**\n"
                    f"**User:** [{first_name}](tg://user?id={user_id})\n"
                    f"**ID:** `{user_id}`\n**Reason:** {gmuted['reason']}\n**Quick Action:** "
                    f"Muted in {msg.chat.title}")
            )
    msg.continue_propagation()
