""" set permissions to users """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from pyrogram import ChatPermissions
from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)


async def is_admin(message: Message):
    check_user = await message.client.get_chat_member(message.chat.id, message.from_user.id)
    user_type = check_user.status
    if user_type == "member":
        return False
    if user_type == "administrator":
        return True
    if user_type == "creator":
        return True
    return False


@userge.on_cmd(
    "lock", about={
        'header': "use this to lock group permissions",
        'description': "Allows you to lock some common permission types in the chat.\n"
                       "[NOTE: Requires proper admin rights in the chat!!!]",
        'types': [
            'all', 'msg', 'media', 'polls', 'invite', 'pin', 'info',
            'webprev', 'inlinebots', 'animations', 'games', 'stickers'],
        'examples': "{tr}lock [all | type]"},
    allow_channels=False, allow_bots=False, allow_private=False)
async def lock_perm(message: Message):
    """
    lock chat permissions from tg group
    """
    if not await is_admin(message):
        await message.edit("Are you even Admin of this chat?")
        return

    msg = ""
    media = ""
    stickers = ""
    animations = ""
    games = ""
    inlinebots = ""
    webprev = ""
    polls = ""
    info = ""
    invite = ""
    pin = ""
    perm = ""

    lock_type = message.input_str
    chat_id = message.chat.id

    if not lock_type:
        await message.edit(text=r"`I Can't Lock Nothing! (－‸ლ)`", del_in=0)
        return

    get_perm = await message.client.get_chat(chat_id)

    msg = get_perm.permissions.can_send_messages
    media = get_perm.permissions.can_send_media_messages
    stickers = get_perm.permissions.can_send_stickers
    animations = get_perm.permissions.can_send_animations
    games = get_perm.permissions.can_send_games
    inlinebots = get_perm.permissions.can_use_inline_bots
    webprev = get_perm.permissions.can_add_web_page_previews
    polls = get_perm.permissions.can_send_polls
    info = get_perm.permissions.can_change_info
    invite = get_perm.permissions.can_invite_users
    pin = get_perm.permissions.can_pin_messages

    if lock_type == "all":
        try:
            await message.client.set_chat_permissions(chat_id, ChatPermissions())
            await message.edit(
                text="**🔒 Locked all permission from this Chat!**", del_in=0)
            await CHANNEL.log(
                f"#LOCK\n\n"
                f"CHAT: `{get_perm.title}` (`{chat_id}`)\n"
                f"PERMISSIONS: `All Permissions`"
            )

        except Exception as e_f:
            await message.edit(
                text=r"`i don't have permission to do that ＞︿＜`\n\n"
                f"**ERROR:** `{e_f}`", del_in=0)

        return

    if lock_type == "msg":
        msg = False
        perm = "messages"

    elif lock_type == "media":
        media = False
        perm = "audios, documents, photos, videos, video notes, voice notes"

    elif lock_type == "stickers":
        stickers = False
        perm = "stickers"

    elif lock_type == "animations":
        animations = False
        perm = "animations"

    elif lock_type == "games":
        games = False
        perm = "games"

    elif lock_type == "inlinebots":
        inlinebots = False
        perm = "inline bots"

    elif lock_type == "webprev":
        webprev = False
        perm = "web page previews"

    elif lock_type == "polls":
        polls = False
        perm = "polls"

    elif lock_type == "info":
        info = False
        perm = "info"

    elif lock_type == "invite":
        invite = False
        perm = "invite"

    elif lock_type == "pin":
        pin = False
        perm = "pin"

    else:
        await message.edit(text=r"`Invalid Lock Type! ¯\_(ツ)_/¯`", del_in=0)
        return

    try:
        await message.client.set_chat_permissions(
            chat_id,
            ChatPermissions(can_send_messages=msg,
                            can_send_media_messages=media,
                            can_send_stickers=stickers,
                            can_send_animations=animations,
                            can_send_games=games,
                            can_use_inline_bots=inlinebots,
                            can_add_web_page_previews=webprev,
                            can_send_polls=polls,
                            can_change_info=info,
                            can_invite_users=invite,
                            can_pin_messages=pin))

        await message.edit(text=f"**🔒 Locked {perm} for this chat!**", del_in=0)
        await CHANNEL.log(
            f"#LOCK\n\n"
            f"CHAT: `{get_perm.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{perm} Permission`"
        )

    except Exception as e_f:
        await message.edit(
            text=r"`i don't have permission to do that ＞︿＜`\n\n"
            f"**ERROR:** `{e_f}`", del_in=0)


@userge.on_cmd("unlock", about={
    'header': "use this to unlock group permissions",
    'description': "Allows you to unlock some common permission types in the chat.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'types': [
        'all', 'msg', 'media', 'polls', 'invite', 'pin', 'info',
        'webprev', 'inlinebots', 'animations', 'games', 'stickers'],
    'examples': "{tr}unlock [all | type]"},
    allow_channels=False, allow_bots=False, allow_private=False)
async def unlock_perm(message: Message):
    """
    unlock chat permissions from tg group
    """
    if not await is_admin(message):
        await message.edit("Are you even Admin of this chat?")
        return

    umsg = ""
    umedia = ""
    ustickers = ""
    uanimations = ""
    ugames = ""
    uinlinebots = ""
    uwebprev = ""
    upolls = ""
    uinfo = ""
    uinvite = ""
    upin = ""
    uperm = ""

    unlock_type = message.input_str
    chat_id = message.chat.id

    if not unlock_type:
        await message.edit(text=r"`I Can't Unlock Nothing! (－‸ლ)`", del_in=0)
        return

    get_uperm = await message.client.get_chat(chat_id)

    umsg = get_uperm.permissions.can_send_messages
    umedia = get_uperm.permissions.can_send_media_messages
    ustickers = get_uperm.permissions.can_send_stickers
    uanimations = get_uperm.permissions.can_send_animations
    ugames = get_uperm.permissions.can_send_games
    uinlinebots = get_uperm.permissions.can_use_inline_bots
    uwebprev = get_uperm.permissions.can_add_web_page_previews
    upolls = get_uperm.permissions.can_send_polls
    uinfo = get_uperm.permissions.can_change_info
    uinvite = get_uperm.permissions.can_invite_users
    upin = get_uperm.permissions.can_pin_messages

    if unlock_type == "all":
        try:
            await message.client.set_chat_permissions(
                chat_id,
                ChatPermissions(can_send_messages=True,
                                can_send_media_messages=True,
                                can_send_stickers=True,
                                can_send_animations=True,
                                can_send_games=True,
                                can_use_inline_bots=True,
                                can_send_polls=True,
                                can_change_info=True,
                                can_invite_users=True,
                                can_pin_messages=True,
                                can_add_web_page_previews=True))

            await message.edit(
                text="**🔓 Unlocked all permission from this Chat!**", del_in=0)
            await CHANNEL.log(
                f"#UNLOCK\n\n"
                f"CHAT: `{get_uperm.title}` (`{chat_id}`)\n"
                f"PERMISSIONS: `All Permissions`")

        except Exception as e_f:
            await message.edit(
                text=r"`i don't have permission to do that ＞︿＜`\n\n"
                f"**ERROR:** `{e_f}`", del_in=0)
        return

    if unlock_type == "msg":
        umsg = True
        uperm = "messages"

    elif unlock_type == "media":
        umedia = True
        uperm = "audios, documents, photos, videos, video notes, voice notes"

    elif unlock_type == "stickers":
        ustickers = True
        uperm = "stickers"

    elif unlock_type == "animations":
        uanimations = True
        uperm = "animations"

    elif unlock_type == "games":
        ugames = True
        uperm = "games"

    elif unlock_type == "inlinebots":
        uinlinebots = True
        uperm = "inline bots"

    elif unlock_type == "webprev":
        uwebprev = True
        uperm = "web page previews"

    elif unlock_type == "polls":
        upolls = True
        uperm = "polls"

    elif unlock_type == "info":
        uinfo = True
        uperm = "info"

    elif unlock_type == "invite":
        uinvite = True
        uperm = "invite"

    elif unlock_type == "pin":
        upin = True
        uperm = "pin"

    else:
        await message.edit(text=r"`Invalid Unlock Type! ¯\_(ツ)_/¯`", del_in=0)
        return

    try:
        await message.client.set_chat_permissions(
            chat_id,
            ChatPermissions(can_send_messages=umsg,
                            can_send_media_messages=umedia,
                            can_send_stickers=ustickers,
                            can_send_animations=uanimations,
                            can_send_games=ugames,
                            can_use_inline_bots=uinlinebots,
                            can_add_web_page_previews=uwebprev,
                            can_send_polls=upolls,
                            can_change_info=uinfo,
                            can_invite_users=uinvite,
                            can_pin_messages=upin))

        await message.edit(text=f"**🔓 Unlocked {uperm} for this chat!**", del_in=0)
        await CHANNEL.log(
            f"#UNLOCK\n\n"
            f"CHAT: `{get_uperm.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{uperm} Permission`"
        )

    except Exception as e_f:
        await message.edit(
            text=r"`i don't have permission to do that ＞︿＜`\n\n"
            f"**ERROR:** `{e_f}`", del_in=0)


@userge.on_cmd("vperm", about={
    'header': "use this to view group permissions",
    'description': "Allows you to view permission types on/off status in the chat."},
    allow_channels=False, allow_bots=False, allow_private=False)
async def view_perm(message: Message):
    """
    check chat permissions from tg group
    """
    if not await is_admin(message):
        await message.edit("Are you even Admin of this chat?")
        return

    v_perm = ""
    vmsg = ""
    vmedia = ""
    vstickers = ""
    vanimations = ""
    vgames = ""
    vinlinebots = ""
    vwebprev = ""
    vpolls = ""
    vinfo = ""
    vinvite = ""
    vpin = ""

    await message.edit("`Checking group permissions... Hang on!! ⏳`")

    v_perm = await message.client.get_chat(message.chat.id)

    def convert_to_emoji(val: bool):
        if val is True:
            return "✅"
        return "❌"

    vmsg = convert_to_emoji(v_perm.permissions.can_send_messages)
    vmedia = convert_to_emoji(v_perm.permissions.can_send_media_messages)
    vstickers = convert_to_emoji(v_perm.permissions.can_send_stickers)
    vanimations = convert_to_emoji(v_perm.permissions.can_send_animations)
    vgames = convert_to_emoji(v_perm.permissions.can_send_games)
    vinlinebots = convert_to_emoji(v_perm.permissions.can_use_inline_bots)
    vwebprev = convert_to_emoji(v_perm.permissions.can_add_web_page_previews)
    vpolls = convert_to_emoji(v_perm.permissions.can_send_polls)
    vinfo = convert_to_emoji(v_perm.permissions.can_change_info)
    vinvite = convert_to_emoji(v_perm.permissions.can_invite_users)
    vpin = convert_to_emoji(v_perm.permissions.can_pin_messages)

    if v_perm is not None:
        try:
            permission_view_str = ""

            permission_view_str += "<b>CHAT PERMISSION INFO:</b>\n\n"
            permission_view_str += f"<b>📩 Send Messages:</b> {vmsg}\n"
            permission_view_str += f"<b>🎭 Send Media:</b> {vmedia}\n"
            permission_view_str += f"<b>🎴 Send Stickers:</b> {vstickers}\n"
            permission_view_str += f"<b>🎲 Send Animations:</b> {vanimations}\n"
            permission_view_str += f"<b>🎮 Can Play Games:</b> {vgames}\n"
            permission_view_str += f"<b>🤖 Can Use Inline Bots:</b> {vinlinebots}\n"
            permission_view_str += f"<b>🌐 Webpage Preview:</b> {vwebprev}\n"
            permission_view_str += f"<b>🗳 Send Polls:</b> {vpolls}\n"
            permission_view_str += f"<b>ℹ Change Info:</b> {vinfo}\n"
            permission_view_str += f"<b>👥 Invite Users:</b> {vinvite}\n"
            permission_view_str += f"<b>📌 Pin Messages:</b> {vpin}\n"

            if v_perm.photo:
                local_chat_photo = await message.client.download_media(
                    message=v_perm.photo.big_file_id
                )

                await message.client.send_photo(chat_id=message.chat.id,
                                                photo=local_chat_photo,
                                                caption=permission_view_str,
                                                parse_mode="html")

                os.remove(local_chat_photo)
                await message.delete()
                await CHANNEL.log("`vperm` command executed")

            else:
                await message.edit(permission_view_str)
                await CHANNEL.log("`vperm` command executed")

        except Exception as e_f:
            await message.edit(
                text="`Something went wrong!` 🤔\n\n"
                f"**ERROR:** `{e_f}`", del_in=0)
