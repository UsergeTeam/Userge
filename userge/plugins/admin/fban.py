""" setup antispam """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved

from UsergeAntiSpamApi import Client
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired, UserAdminInvalid, ChannelInvalid)

from userge import userge, Message, Config, get_collection, pool

FBAN_USERS = get_collection("FBAN_USERS")

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)

client = None


async def _init() -> None:
    if Config.USERGE_ANTISPAM_API:
        try:
            client = await pool.run_in_thread(Client)(Config.USERGE_ANTISPAM_API)
        except Exception as err:
            await CHANNEL.log(err)
            LOG.error(err)


def check_client(func):
    async def wrapper(msg: Message):
        if client:
            await func(msg)
        else:
            await msg.err("USERGE_ANTISPAM_API not found!")
    return wrapper


@userge.on_cmd("fban", about={
    'header': "Fban User in Userge AntiSpam Api",
    'usage': "{tr}fban [user id | username | reply to user] [reason]",
    'examples': "{tr}fban 777000 reason"
}, allow_channels=False, allow_bots=False)
@check_client
async def fban(msg: Message):
    user_id, reason = msg.extract_user_and_text
    if not user_id:
        return await msg.err("user id not found!")
    elif not reason:
        return await msg.err("reason not found!")
    elif await FBAN_USERS.find_one({"user_id": user_id}):
        return await msg.err("this user is already fbanned!")
    else:
        try:
            await pool.run_in_thread(client.add_ban)(user_id, reason)
        except Exception as err:
            await msg.err(err)
        else:
            user = await msg.client.get_user_dict(user_id)
            name = user['first_name']
            if msg.client.is_bot:
                chats = [msg.chat]
            else:
                chats = await msg.client.get_common_chats(user_id)
            fbanned_chats = []
            c_n = []
            for chat in chats:
                try:
                    await chat.kick_member(user_id)
                    c_n.apppend(chat.title)
                    fbanned_chats.append(chat.id)
                except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
                    pass
            await CHANNEL.log(
                r"\\**#Antispam_Log**//"
                f"\n**User:** [{name}](tg://user?id={user_id})\n"
                f"**User ID:** `{user_id}`\n"
                f"**Chat names:** {', '.join(c_n)}\n"
                f"**Chat IDs:** `{', '.join(fbanned_chats)}`\n"
                f"**Reason:** `{reason}`\n\n$FBAN #id{user_id}"
            )
            await FBAN_USERS.insert_one(
                {'name': name,
                 'user_id': user_id,
                 'reason': reason,
                 'chat_ids': fbanned_chats}
            )
            if msg.reply_to_msg:
                await CHANNEL.fwd_msg(msg.reply_to_msg)
                await CHANNEL.log(f'$FBAN #prid{user_id} ⬆️')
            LOG.info("F-Banned %s", str(user_id))


@userge.on_cmd("unfban", about={
    'header': "UnFban User in Userge AntiSpam Api",
    'usage': "{tr}unfban [user id | username | reply to user]",
    'examples': "{tr}unfban 777000"
}, allow_channels=False, allow_bots=False)
@check_client
async def unfban(msg: Message):
    user_id, _ = msg.extract_user_and_text
    if not user_id:
        return await msg.err("user id not found!")
    else:
        try:
            await pool.run_in_thread(client.delete_ban)(user_id)
        except Exception as err:
            await msg.err(err)
        else:
            found = await FBAN_USERS.find_one({'user_id': user_id})
            if not found:
                await msg.err("User Not Found in My Fban List")
                return
            user = await msg.client.get_user_dict(user_id)
            name = user['first_name']
            if 'chat_ids' in found:
                for chat_id in found['chat_ids']:
                    try:
                        await userge.unban_chat_member(chat_id, user_id)
                        await CHANNEL.log(
                            r"\\**#Antispam_Log**//"
                            f"\n**User:** [{name}](tg://user?id={user_id})\n"
                            f"**User ID:** `{user_id}`\n\n"
                            f"$UNFBAN #id{user_id}")
                    except (ChatAdminRequired, UserAdminInvalid, ChannelInvalid):
                        pass
            await msg.edit(r"\\**#UnFbanned_User**//"
                            f"\n\n**First Name:** [{name}](tg://user?id={user_id})\n"
                            f"**User ID:** `{user_id}`")
            await FBAN_USERS.delete_one({'name': name, 'user_id': user_id})
            LOG.info("UnFbanned %s", str(user_id))


@userge.on_cmd("flist", about={
    'header': "List Fbanned Users by you in Userge AntiSpam Api",
    'usage': "{tr}flist",
    'examples': "{tr}fban"
}, allow_channels=False, allow_bots=False)
@check_client
async def list_fbanned_users(msg: Message):
    """ List fbanned users by you """
    msg = ''

    async for c in FBAN_USERS.find():
        msg += (
            f"**User:** [{c['name']}](tg://user?id={c['user_id']})\n"
            f"**User Id:** `{c['user_id']}`\n"
            f"**Reason:** `{c['reason']}`\n\n"
        )

    await msg.edit_or_send_as_file(
        f"**--Fbanned Banned Users List--**\n\n{msg}"
        if msg else "`Fbanned users list empty!`"
    )


@userge.on_cmd("fstatus", about={
    'header': "Check fbanned status of user in Userge antispam",
    'usage': "{tr}fstatus [user id | username | reply to user]",
    'examples': "{tr}fban 777000"
}, allow_channels=False, allow_bots=False)
@check_client
async def fstatus(msg: Message):
    user_id, _ = msg.extract_user_and_text
    if not user_id:
        return await msg.err("user id not found!")
    else:
        try:
            ban = await pool.run_in_thread(client.getban)(user_id)
            if ban:
                msg = (
                    "#FBan_Found\n"
                    "**User:** "
                    f"[{ban.name}](tg://user?id={ban.user_id})\n"
                    f"**User ID:** `{ban.user_id}`\n"
                    f"**Date:** `{ban.date}`\n"
                    "**Admin:** "
                    f"[{ban.admin.name}](tg://user?id={ban.admin.user_id})"
                )
            else:
                msg = "This User is not banned!"
            await msg.reply(msg)
        except Exception as err:
            await msg.err(err)