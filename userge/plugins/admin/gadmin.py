# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import time
from userge import userge, Message
from pyrogram import ChatPermissions

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("promote", about="""\
__use this to promote group members__

**Usage:**

`Provides admin rights to the person in the supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.promote [username | userid] or [reply to user]`""")

async def promote_usr(message: Message):
    """
    this function can promote members in tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    promote_perm = check_admin.can_promote_members

    await message.edit("`Trying to Promote User.. Hang on!`")

    if promote_perm:

        user_id = message.input_str

        if user_id:

            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)

                await message.edit("**👑 Promoted Successfully**", del_in=0)

                await CHANNEL.log(
                    f"#PROMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help promote for more info`", del_in=0)

        elif message.reply_to_message:

            get_mem = await userge.get_chat_member(chat_id, message.reply_to_message.from_user.id)

            try:
                await userge.promote_chat_member(chat_id, get_mem.user.id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)

                await message.edit("**👑 Promoted Successfully**", del_in=0)

                await CHANNEL.log(
                    f"#PROMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help promote for more info`", del_in=0)

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help promote for more info`", del_in=0)

            return

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=0)


@userge.on_cmd("demote", about="""\
__use this to demote group members__

**Usage:**

`Remove admin rights from admin in the supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.demote [username | userid] or [reply to user]`""")

async def demote_usr(message: Message):
    """
    this function can demote members in tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    demote_perm = check_admin.can_promote_members

    await message.edit("`Trying to Demote User.. Hang on!`")

    if demote_perm:

        user_id = message.input_str

        if user_id:

            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("**🛡 Demoted Successfully**", del_in=0)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help demote for more info`", del_in=0)

        elif message.reply_to_message:

            get_mem = await userge.get_chat_member(chat_id, message.reply_to_message.from_user.id)

            try:
                await userge.promote_chat_member(chat_id, get_mem.user.id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("**🛡 Demoted Successfully**", del_in=0)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help demote for more info`", del_in=0)

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help demote for more info`", del_in=0)

            return

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=0)

@userge.on_cmd("ban", about="""\
__use this to ban group members__

**Usage:**

`Ban member form supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.ban [username | userid] or [reply to user] <reason (optional)>`""")

async def ban_usr(message: Message):
    """
    this function can ban user from tg group
    """
    reason = ""
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    ban_perm = check_admin.can_restrict_members

    if ban_perm:

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = message.input_str
        else:
            args = message.input_str.split(maxsplit=1)
            if len(args) == 2:
                user_id, reason = args
            elif len(args) == 1:
                user_id = args[0]
            else:
                await message.edit(
                    text="`no valid user_id or message specified,`"
                    "`do .help ban for more info`", del_in=0)
                return
        if user_id:
            get_mem = await userge.get_chat_member(chat_id, user_id)
            await userge.kick_chat_member(chat_id, user_id)
            await message.edit(
                f"#BAN\n\n"
                f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                f"(`{get_mem.user.id}`)\n"
                f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                f"REASON: `{reason}`", log=True)

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=0)

@userge.on_cmd("unban", about="""\
__use this to unban group members__

**Usage:**

`Unban member form supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.unban <username/userid> (or) reply to a message with .unban`""")

async def unban_usr(message: Message):
    """
    this function can unban user from tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    unban_perm = check_admin.can_restrict_members

    if unban_perm:

        user_id = message.input_str

        if user_id:
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.unban_chat_member(chat_id, user_id)
                await message.edit("**🛡 Successfully Unbanned**", del_in=0)
                await CHANNEL.log(
                    f"#UNBAN\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help unban for more info`", del_in=0)

        elif message.reply_to_message:

            get_mem = await userge.get_chat_member(chat_id, message.reply_to_message.from_user.id)

            try:
                await userge.unban_chat_member(chat_id, get_mem.user.id)
                await message.edit("**🛡 Successfully Unbanned**", del_in=0)
                await CHANNEL.log(
                    f"#UNBAN\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help unabn for more info`", del_in=0)

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help unban for more info`", del_in=0)

            return

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=5)

@userge.on_cmd("mute", about="""\
__use this to mute group members__

**Usage:**

`Mute member in the supergroup. you can only use one flag for command`

[NOTE: Requires proper admin rights in the chat!!!]

**Available Flags:**
`-m` : __minutes__
`-h` : __hours__
`-d` : __days__


**Example:**

    `.mute -flag [username | userid] or [reply to user] :reason (optional)`
    `.mute -d1 @someusername/userid/replytouser spam` (mute for one day)""")

async def mute_usr(message: Message):
    """
    this function can mute user from tg group
    """
    reason = ""
    chat_id = message.chat.id
    flags = message.flags
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    mute_perm = check_admin.can_restrict_members

    minutes = int(flags.get('-m', 0))
    hours = int(flags.get('-h', 0))
    days = int(flags.get('-d', 0))

    await message.edit("`Trying to Mute User.. Hang on!`")

    if mute_perm:

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = message.filtered_input_str
        else:
            args = message.filtered_input_str.split(maxsplit=1)
            if len(args) == 2:
                user_id, reason = args
            elif len(args) == 1:
                user_id = args[0]
            else:
                await message.edit(
                    text="`no valid user_id or message specified,`"
                    "`do .help mute for more info`", del_in=0)
                return

        if minutes:
            get_mem = await userge.get_chat_member(chat_id, user_id)
            mute_period = minutes * 60

            try:
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{minutes} minutes`\n"
                    f"REASON: `{reason}`", log=True)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n"
                    f"**ERROR**: {e}", del_in=0)

        elif hours:
            get_mem = await userge.get_chat_member(chat_id, user_id)
            mute_period = hours * 3600

            try:
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{hours} hours`\n"
                    f"REASON: `{reason}`", log=True)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n"
                    f"**ERROR**: {e}", del_in=0)

        elif days:
            get_mem = await userge.get_chat_member(chat_id, user_id)
            mute_period = hours * 86400

            try:
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{days} days`\n"
                    f"REASON: `{reason}`", log=True)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n"
                    f"**ERROR**: {e}", del_in=0)

        else:
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `forever`\n"
                    f"REASON: `{reason}`", log=True)

            except Exception as e:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n"
                    f"**ERROR**: {e}", del_in=0)

            return

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=5)

@userge.on_cmd("unmute", about="""\
__use this to unmute group members__

**Usage:**

`Unmute member form supergroup.`

[NOTE: Requires proper admin rights in the chat!!!]


**Example:**

    `.unmute <username/userid> (or) reply to a message with .unmute`""")

async def unmute_usr(message: Message):
    """
    this function can unmute user from tg group
    """
    chat_id = message.chat.id
    check_admin = await userge.get_chat_member(chat_id, message.from_user.id)
    get_group = await userge.get_chat(chat_id)
    unmute_perm = check_admin.can_restrict_members

    amsg = get_group.permissions.can_send_messages
    amedia = get_group.permissions.can_send_media_messages
    astickers = get_group.permissions.can_send_stickers
    aanimations = get_group.permissions.can_send_animations
    agames = get_group.permissions.can_send_games
    ainlinebots = get_group.permissions.can_use_inline_bots
    awebprev = get_group.permissions.can_add_web_page_previews
    apolls = get_group.permissions.can_send_polls
    ainfo = get_group.permissions.can_change_info
    ainvite = get_group.permissions.can_invite_users
    apin = get_group.permissions.can_pin_messages

    if unmute_perm:

        user_id = message.input_str

        if user_id:
            get_mem = await userge.get_chat_member(chat_id, user_id)

            try:
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(
                                                      can_send_messages=amsg,
                                                      can_send_media_messages=amedia,
                                                      can_send_stickers=astickers,
                                                      can_send_animations=aanimations,
                                                      can_send_games=agames,
                                                      can_use_inline_bots=ainlinebots,
                                                      can_add_web_page_previews=awebprev,
                                                      can_send_polls=apolls,
                                                      can_change_info=ainfo,
                                                      can_invite_users=ainvite,
                                                      can_pin_messages=apin))

                await message.edit("**🛡 Successfully Unmuted**", del_in=0)
                await CHANNEL.log(
                    f"#UNMUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help unmute for more info`", del_in=0)

        elif message.reply_to_message:

            get_mem = await userge.get_chat_member(chat_id, message.reply_to_message.from_user.id)

            try:
                await userge.restrict_chat_member(chat_id, get_mem.user.id,
                                                  ChatPermissions(
                                                      can_send_messages=amsg,
                                                      can_send_media_messages=amedia,
                                                      can_send_stickers=astickers,
                                                      can_send_animations=aanimations,
                                                      can_send_games=agames,
                                                      can_use_inline_bots=ainlinebots,
                                                      can_add_web_page_previews=awebprev,
                                                      can_send_polls=apolls,
                                                      can_change_info=ainfo,
                                                      can_invite_users=ainvite,
                                                      can_pin_messages=apin))

                await message.edit("**🛡 Successfully Unmuted**", del_in=0)
                await CHANNEL.log(
                    f"#UNMUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except:
                await message.edit(
                    text="`something went wrong 🤔,`"
                    "`do .help unmute for more info`", del_in=0)

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help unmute for more info`", del_in=0)

            return

    else:
        await message.edit(
            text="`Looks like i don't have proper admin permission to do that ⚠`", del_in=0)
