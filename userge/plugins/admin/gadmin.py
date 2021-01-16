""" manage your group """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import time
import asyncio

from emoji import get_emoji_regexp
from pyrogram.types import ChatPermissions
from pyrogram.errors import (
    FloodWait, UserAdminInvalid, UsernameInvalid, PeerIdInvalid, UserIdInvalid)

from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("promote", about={
    'header': "use this to promote group members",
    'description': "Provides admin rights to the person in the supergroup.\n"
                   "you can also add custom title while promoting new admin.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': [
        "{tr}promote [username | userid] or [reply to user] :custom title (optional)",
        "{tr}promote @someusername/userid/replytouser Staff (custom title)"]},
    allow_channels=False, check_promote_perm=True)
async def promote_usr(message: Message):
    """ promote members in tg group """
    chat_id = message.chat.id
    await message.edit("`Trying to Promote User.. Hang on!! ⏳`")
    user_id, custom_rank = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help promote for more info`", del_in=5)
        return
    if custom_rank:
        custom_rank = get_emoji_regexp().sub(u'', custom_rank)
        if len(custom_rank) > 15:
            custom_rank = custom_rank[:15]
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.promote_chat_member(chat_id, user_id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)
        if custom_rank:
            await asyncio.sleep(2)
            await message.client.set_administrator_title(chat_id, user_id, custom_rank)
        await message.edit("`👑 Promoted Successfully..`", del_in=5)
        await CHANNEL.log(
            "#PROMOTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CUSTOM TITLE: `{custom_rank or None}`\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)")
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`something went wrong! 🤔`\n\n**ERROR:** `{e_f}`")


@userge.on_cmd("demote", about={
    'header': "use this to demote group members",
    'description': "Remove admin rights from admin in the supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}demote [username | userid] or [reply to user]"},
    allow_channels=False, check_promote_perm=True)
async def demote_usr(message: Message):
    """ demote members in tg group """
    chat_id = message.chat.id
    await message.edit("`Trying to Demote User.. Hang on!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help demote for more info` ⚠", del_in=5)
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.promote_chat_member(chat_id, user_id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)
        await message.edit("`🛡 Demoted Successfully..`", del_in=5)
        await CHANNEL.log(
            "#DEMOTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)")
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`something went wrong! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("ban", about={
    'header': "use this to ban group members",
    'description': "Ban member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'flags': {
        '-m': "minutes",
        '-h': "hours",
        '-d': "days"},
    'examples': "{tr}ban [flag] [username | userid] or [reply to user] :reason (optional)"},
    allow_channels=False, check_restrict_perm=True)
async def ban_user(message: Message):
    """ ban user from tg group """
    await message.edit("`Trying to Ban User.. Hang on!! ⏳`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help ban for more info`", del_in=5)
        return

    chat_id = message.chat.id
    flags = message.flags
    minutes = int(flags.get('-m', 0))
    hours = int(flags.get('-h', 0))
    days = int(flags.get('-d', 0))

    ban_period = 0
    _time = "forever"
    if minutes:
        ban_period = time.time() + minutes * 60
        _time = f"{minutes}m"
    elif hours:
        ban_period = time.time() + hours * 3600
        _time = f"{hours}h"
    elif days:
        ban_period = time.time() + days * 86400
        _time = f"{days}d"

    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.kick_chat_member(chat_id, user_id, int(ban_period))
        await message.edit(
            "#BAN\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"TIME: `{_time}`\n"
            f"REASON: `{reason}`", log=__name__)
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(
            "`something went wrong 🤔, do .help ban for more info`\n\n"
            f"**ERROR**: `{e_f}`", del_in=5)


@userge.on_cmd("unban", about={
    'header': "use this to unban group members",
    'description': "Unban member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}unban [username | userid] or [reply to user]"},
    allow_channels=False, check_restrict_perm=True)
async def unban_usr(message: Message):
    """ unban user from tg group """
    chat_id = message.chat.id
    await message.edit("`Trying to Unban User.. Hang on!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help unban for more info` ⚠", del_in=5)
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.unban_chat_member(chat_id, user_id)
        await message.edit("`🛡 Successfully Unbanned..`", del_in=5)
        await CHANNEL.log(
            "#UNBAN\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)")
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit("`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`something went wrong! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("kick", about={
    'header': "use this to kick group members",
    'description': "Kick member from supergroup. member can rejoin the group again if they want.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}kick [username | userid] or [reply to user]"},
    allow_channels=False, check_restrict_perm=True)
async def kick_usr(message: Message):
    """ kick user from tg group """
    chat_id = message.chat.id
    await message.edit("`Trying to Kick User.. Hang on!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help kick for more info` ⚠", del_in=5)
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.kick_chat_member(chat_id, user_id, int(time.time() + 60))
        await message.edit(
            "#KICK\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)", log=__name__)
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit(
            "`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`something went wrong! 🤔`\n\n**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("mute", about={
    'header': "use this to mute group members",
    'description': "Mute member in the supergroup. you can only use one flag for command.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'flags': {
        '-m': "minutes",
        '-h': "hours",
        '-d': "days"},
    'examples': [
        "{tr}mute -flag [username | userid] or [reply to user] :reason (optional)",
        "{tr}mute -d1 @someusername/userid/replytouser SPAM (mute for one day:reason SPAM)"]},
    allow_channels=False, check_restrict_perm=True)
async def mute_usr(message: Message):
    """ mute user from tg group """
    chat_id = message.chat.id
    flags = message.flags
    minutes = flags.get('-m', 0)
    hours = flags.get('-h', 0)
    days = flags.get('-d', 0)
    await message.edit("`Trying to Mute User.. Hang on!! ⏳`")
    user_id, reason = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help mute for more info`", del_in=5)
        return
    if minutes:
        mute_period = int(minutes) * 60
        _time = f"{int(minutes)}m"
    elif hours:
        mute_period = int(hours) * 3600
        _time = f"{int(hours)}h"
    elif days:
        mute_period = int(days) * 86400
        _time = f"{int(days)}d"
    if flags:
        try:
            get_mem = await message.client.get_chat_member(chat_id, user_id)
            await message.client.restrict_chat_member(
                chat_id, user_id,
                ChatPermissions(),
                int(time.time() + mute_period))
            await message.edit(
                "#MUTE\n\n"
                f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                f"(`{get_mem.user.id}`)\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"MUTE UNTIL: `{_time}`\n"
                f"REASON: `{reason}`", log=__name__)
        except UsernameInvalid:
            await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
        except PeerIdInvalid:
            await message.edit(
                "`invalid username or userid, try again with valid info ⚠`", del_in=5)
        except UserIdInvalid:
            await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
        except Exception as e_f:
            await message.edit(
                "`something went wrong 🤔, do .help mute for more info`\n\n"
                f"**ERROR**: `{e_f}`", del_in=5)
    else:
        try:
            get_mem = await message.client.get_chat_member(chat_id, user_id)
            await message.client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await message.edit(
                "#MUTE\n\n"
                f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                f"(`{get_mem.user.id}`)\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"MUTE UNTIL: `forever`\n"
                f"REASON: `{reason}`", log=__name__)
        except UsernameInvalid:
            await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
        except PeerIdInvalid:
            await message.edit(
                "`invalid username or userid, try again with valid info ⚠`", del_in=5)
        except UserIdInvalid:
            await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
        except Exception as e_f:
            await message.edit(
                "`something went wrong 🤔, do .help mute for more info`\n\n"
                f"**ERROR**: {e_f}", del_in=5)


@userge.on_cmd("unmute", about={
    'header': "use this to unmute group members",
    'description': "Unmute member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}unmute [username | userid]  or [reply to user]"},
    allow_channels=False, check_restrict_perm=True)
async def unmute_usr(message: Message):
    """ unmute user from tg group """
    chat_id = message.chat.id
    await message.edit("`Trying to Unmute User.. Hang on!! ⏳`")
    user_id, _ = message.extract_user_and_text
    if not user_id:
        await message.edit(
            text="`no valid user_id or message specified,`"
            "`do .help unmute for more info`", del_in=5)
        return
    try:
        get_mem = await message.client.get_chat_member(chat_id, user_id)
        await message.client.unban_chat_member(chat_id, user_id)
        await message.edit("`🛡 Successfully Unmuted..`", del_in=5)
        await CHANNEL.log(
            "#UNMUTE\n\n"
            f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
            f"(`{get_mem.user.id}`)\n"
            f"CHAT: `{message.chat.title}` (`{chat_id}`)")
    except UsernameInvalid:
        await message.edit("`invalid username, try again with valid info ⚠`", del_in=5)
    except PeerIdInvalid:
        await message.edit("`invalid username or userid, try again with valid info ⚠`", del_in=5)
    except UserIdInvalid:
        await message.edit("`invalid userid, try again with valid info ⚠`", del_in=5)
    except Exception as e_f:
        await message.edit(f"`something went wrong!` 🤔\n\n**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("zombies", about={
    'header': "use this to clean zombie accounts",
    'description': "check & remove zombie (deleted) accounts from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'flags': {'-c': "clean"},
    'examples': [
        "{tr}zombies [check deleted accounts in group]",
        "{tr}zombies -c [remove deleted accounts from group]"]},
    allow_channels=False, allow_bots=False, allow_private=False)
async def zombie_clean(message: Message):
    """ remove deleted accounts from tg group """
    chat_id = message.chat.id
    check_user = await message.client.get_chat_member(message.chat.id, message.from_user.id)
    flags = message.flags
    rm_delaccs = '-c' in flags
    can_clean = check_user.status in ("administrator", "creator")
    if rm_delaccs:
        del_users = 0
        del_admins = 0
        del_total = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"
        if can_clean:
            await message.edit("`Hang on!! cleaning zombie accounts from this chat..`")
            async for member in message.client.iter_chat_members(chat_id):
                if member.user.is_deleted:
                    try:
                        await message.client.kick_chat_member(
                            chat_id,
                            member.user.id, int(time.time() + 45))
                    except UserAdminInvalid:
                        del_users -= 1
                        del_admins += 1
                    except FloodWait as e_f:
                        time.sleep(e_f.x)
                    del_users += 1
                    del_total += 1
            if del_admins > 0:
                del_stats = f"`👻 Found` **{del_total}** `total zombies..`\
                \n`🗑 Cleaned` **{del_users}** `zombie (deleted) accounts from this chat..`\
                \n🛡 **{del_admins}** `deleted admin accounts are skipped!!`"
            else:
                del_stats = f"`👻 Found` **{del_total}** `total zombies..`\
                \n`🗑 Cleaned` **{del_users}** `zombie (deleted) accounts from this chat..`"
            await message.edit(f"{del_stats}", del_in=5)
            await CHANNEL.log(
                "#ZOMBIE_CLEAN\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"TOTAL ZOMBIE COUNT: `{del_total}`\n"
                f"CLEANED ZOMBIE COUNT: `{del_users}`\n"
                f"ZOMBIE ADMIN COUNT: `{del_admins}`")
        else:
            await message.edit(r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=5)
    else:
        del_users = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"
        await message.edit("`🔎 Searching for zombie accounts in this chat..`")
        async for member in message.client.iter_chat_members(chat_id):
            if member.user.is_deleted:
                del_users += 1
        if del_users > 0:
            del_stats = f"`Found` **{del_users}** `zombie accounts in this chat.`"
            await message.edit(
                f"🕵️‍♂️ {del_stats} `you can clean them using .zombies -c`", del_in=5)
            await CHANNEL.log(
                "#ZOMBIE_CHECK\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"ZOMBIE COUNT: `{del_users}`")
        else:
            await message.edit(f"{del_stats}", del_in=5)
            await CHANNEL.log(
                "#ZOMBIE_CHECK\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                r"ZOMBIE COUNT: `WOOHOO group is clean.. \^o^/`")


@userge.on_cmd("pin", about={
    'header': "use this to pin & unpin messages",
    'description': "pin & unpin messages in groups with or without notify to members.",
    'flags': {
        '-s': "silent",
        '-u': "unpin"},
    'examples': [
        "{tr}pin [reply to chat message]",
        "{tr}pin -s [reply to chat message]",
        "{tr}pin -u [send to chat]"]},
    allow_channels=False, check_pin_perm=True)
async def pin_msgs(message: Message):
    """ pin & unpin message in groups """
    chat_id = message.chat.id
    flags = message.flags
    disable_notification = False
    if '-s' in flags:
        disable_notification = True
    unpin_pinned = '-u' in flags
    if unpin_pinned:
        try:
            if message.reply_to_message:
                await message.client.unpin_chat_message(
                    chat_id, message.reply_to_message.message_id)
            else:
                await message.client.unpin_all_chat_messages(chat_id)
            await message.delete()
            await CHANNEL.log(
                f"#UNPIN\n\nCHAT: `{message.chat.title}` (`{chat_id}`)")
        except Exception as e_f:
            await message.edit(
                r"`something went wrong! (⊙_⊙;)`"
                "\n`do .help pin for more info..`\n\n"
                f"**ERROR:** `{e_f}`")
    else:
        try:
            message_id = message.reply_to_message.message_id
            await message.client.pin_chat_message(
                chat_id, message_id, disable_notification=disable_notification)
            await message.delete()
            await CHANNEL.log(
                f"#PIN\n\nCHAT: `{message.chat.title}` (`{chat_id}`)")
        except Exception as e_f:
            await message.edit(
                r"`something went wrong! (⊙_⊙;)`"
                "\n`do .help pin for more info..`\n\n"
                f"**ERROR:** `{e_f}`")


@userge.on_cmd("gpic", about={
    'header': "use this to set or delete chat photo",
    'description': "set new chat photo or delete current chat photo",
    'flags': {
        '-s': "set",
        '-d': "delete"},
    'examples': [
        "{tr}gpic -s [reply to chat image/media file]",
        "{tr}gpic -d [send to chat]"]},
    allow_channels=False, check_change_info_perm=True)
async def chatpic_func(message: Message):
    """ change chat photo """
    chat_id = message.chat.id
    flags = message.flags
    gpic_set = '-s' in flags
    gpic_del = '-d' in flags
    if gpic_set:
        if message.reply_to_message.photo:
            try:
                img_id = message.reply_to_message.photo.file_id
                await message.client.set_chat_photo(
                    chat_id=chat_id, photo=img_id)
                await message.delete()
                await CHANNEL.log(
                    f"#GPIC-SET\n\nCHAT: `{message.chat.title}` (`{chat_id}`)")
            except Exception as e_f:
                await message.edit(
                    r"`something went wrong!! (⊙ˍ⊙)`"
                    f"\n\n**ERROR:** `{e_f}`")
        elif message.reply_to_message.document.mime_type == "image/png":
            try:
                gpic_path = await message.client.download_media(message.reply_to_message)
                await message.client.set_chat_photo(chat_id=message.chat.id, photo=gpic_path)
                await message.delete()
                os.remove(gpic_path)
                await CHANNEL.log(
                    f"#GPIC-SET\n\nCHAT: `{message.chat.title}` (`{chat_id}`)")
            except Exception as e_f:
                await message.edit(
                    r"`something went wrong!! (⊙ˍ⊙)`"
                    f"\n\n**ERROR:** `{e_f}`")
        else:
            await message.edit(
                text="`no valid message/picture reply specified,`"
                " `do .help gpic for more info` ⚠", del_in=5)
    elif gpic_del:
        try:
            await message.client.delete_chat_photo(chat_id)
            await message.delete()
            await CHANNEL.log(
                f"#GPIC-DELETE\n\nCHAT: `{message.chat.title}` (`{chat_id}`)")
        except Exception as e_f:
            await message.edit(
                r"`something went wrong!! (⊙ˍ⊙)`"
                f"\n\n**ERROR:** `{e_f}`")
    else:
        await message.edit("`invalid flag type, do .help gpic for more info` ⚠", del_in=5)


@userge.on_cmd("smode", about={
    'header': "turn on/off chat slow mode",
    'description': "use this to turn off or switch between chat slow mode \n"
                   "available 6 modes, s10/s30/m1/m5/m15/h1",
    'flags': {
        '-s': "seconds",
        '-m': "minutes",
        '-h': "hour",
        '-o': "off"},
    'types': [
        '-s10 = 10 seconds', '-s30 = 30 seconds', '-m1 = 1 minutes',
        '-m5 = 5 minutes', '-m15 = 15 minutes', '-h1 = 1 hour'],
    'examples': [
        "{tr}smode -s30 [send to chat] (turn on 30s slow mode) ",
        "{tr}smode -o [send to chat] (turn off slow mode)"]},
    allow_channels=False, check_promote_perm=True)
async def smode_switch(message: Message):
    """ turn on/off chat slow mode """
    chat_id = message.chat.id
    flags = message.flags
    seconds = flags.get('-s', 0)
    minutes = flags.get('-m', 0)
    hours = flags.get('-h', 0)
    smode_off = '-o' in flags
    if seconds:
        try:
            seconds = int(seconds)
            await message.client.set_slow_mode(chat_id, seconds)
            await message.edit(
                f"`⏳ turned on {seconds} seconds slow mode for chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{seconds} seconds`")
        except Exception as e_f:
            await message.edit(
                "`something went wrong!!, do .help smode for more info..` \n\n"
                f"**ERROR:** `{e_f}`")
    elif minutes:
        try:
            smode_time = int(minutes) * 60
            await message.client.set_slow_mode(chat_id, smode_time)
            await message.edit(f"`⏳ turned on {minutes} minutes slow mode for chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{minutes} minutes`")
        except Exception as e_f:
            await message.edit(
                "`something went wrong!!, do .help smode for more info..` \n\n"
                f"**ERROR:** `{e_f}`")
    elif hours:
        try:
            smode_time = int(hours) * 3600
            await message.client.set_slow_mode(chat_id, smode_time)
            await message.edit("`⏳ turned on 1 hour slow mode for chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\n"
                f"CHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"SLOW MODE TIME: `{hours} hours`")
        except Exception as e_f:
            await message.edit(
                "`something went wrong!!, do .help smode for more info..` \n\n"
                f"**ERROR:** `{e_f}`")
    elif smode_off:
        try:
            await message.client.set_slow_mode(chat_id, 0)
            await message.edit("`⏳ turned off slow mode for chat!`", del_in=5)
            await CHANNEL.log(
                f"#SLOW_MODE\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\nSLOW MODE: `Off`")
        except Exception as e_f:
            await message.edit(
                f"`something went wrong!!, do .help smode for more info..` \n\n**ERROR:** `{e_f}`")
    else:
        await message.edit("`inavlid flag type/mode.. do .help smode for more info!!`", del_in=5)
