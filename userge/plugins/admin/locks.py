""" set permissions to users """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from typing import Sequence

from pyrogram.types import ChatPermissions

from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)

_types = [
    'msg', 'media', 'polls', 'invite', 'pin', 'info',
    'webprev', 'inlinebots', 'animations', 'games', 'stickers'
]


def _get_chat_lock(message: Message, lock_type: str, should_lock: bool) -> Sequence[str]:
    if should_lock is True:
        lock = False
    else:
        lock = True
    msg = message.chat.permissions.can_send_messages
    media = message.chat.permissions.can_send_media_messages
    stickers = message.chat.permissions.can_send_stickers
    animations = message.chat.permissions.can_send_animations
    games = message.chat.permissions.can_send_games
    inlinebots = message.chat.permissions.can_use_inline_bots
    webprev = message.chat.permissions.can_add_web_page_previews
    polls = message.chat.permissions.can_send_polls
    info = message.chat.permissions.can_change_info
    invite = message.chat.permissions.can_invite_users
    pin = message.chat.permissions.can_pin_messages
    perm = None

    if lock_type == "msg":
        msg = lock
        perm = "messages"
    elif lock_type == "media":
        media = lock
        perm = "audios, documents, photos, videos, video notes, voice notes"
    elif lock_type == "stickers":
        stickers = lock
        perm = "stickers"
    elif lock_type == "animations":
        animations = lock
        perm = "animations"
    elif lock_type == "games":
        games = lock
        perm = "games"
    elif lock_type == "inlinebots":
        inlinebots = lock
        perm = "inline bots"
    elif lock_type == "webprev":
        webprev = lock
        perm = "web page previews"
    elif lock_type == "polls":
        polls = lock
        perm = "polls"
    elif lock_type == "info":
        info = lock
        perm = "info"
    elif lock_type == "invite":
        invite = lock
        perm = "invite"
    elif lock_type == "pin":
        pin = lock
        perm = "pin"
    return (
        msg, media, stickers,
        animations, games, inlinebots,
        webprev, polls, info,
        invite, pin, perm)


@userge.on_cmd(
    "lock", about={
        'header': "use this to lock group permissions",
        'description': "Allows you to lock some common permission types in the chat.\n"
                       "[NOTE: Requires proper admin rights in the chat!!!]",
        'types': [
            'all', 'msg', 'media', 'polls', 'invite', 'pin', 'info',
            'webprev', 'inlinebots', 'animations', 'games', 'stickers'],
        'examples': "{tr}lock [all | type]"},
    allow_channels=False, check_restrict_perm=True)
async def lock_perm(message: Message):
    """ lock chat permissions from tg group """
    lock_type = message.input_str
    chat_id = message.chat.id
    if not lock_type:
        await message.err(r"I Can't Lock Nothing! (－‸ლ)")
        return
    if lock_type == "all":
        try:
            await message.client.set_chat_permissions(chat_id, ChatPermissions())
            await message.edit("**🔒 Locked all permission from this Chat!**", del_in=5)
            await CHANNEL.log(
                f"#LOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"PERMISSIONS: `All Permissions`")
        except Exception as e_f:
            await message.edit(
                r"`i don't have permission to do that ＞︿＜`\n\n"
                f"**ERROR:** `{e_f}`", del_in=5)
        return
    if lock_type in _types:
        (msg, media, stickers,
         animations, games, inlinebots,
         webprev, polls, info, invite,
         pin, perm) = _get_chat_lock(message, lock_type, True)
    else:
        await message.err(r"Invalid lock type! ¯\_(ツ)_/¯")
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
        await message.edit(f"**🔒 Locked {perm} for this chat!**", del_in=5)
        await CHANNEL.log(
            f"#LOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{perm} Permission`")
    except Exception as e_f:
        await message.edit(
            r"`i don't have permission to do that ＞︿＜`\n\n"
            f"**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("unlock", about={
    'header': "use this to unlock group permissions",
    'description': "Allows you to unlock some common permission types in the chat.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'types': [
        'all', 'msg', 'media', 'polls', 'invite', 'pin', 'info',
        'webprev', 'inlinebots', 'animations', 'games', 'stickers'],
    'examples': "{tr}unlock [all | type]"},
    allow_channels=False, check_restrict_perm=True)
async def unlock_perm(message: Message):
    """ unlock chat permissions from tg group """
    unlock_type = message.input_str
    chat_id = message.chat.id
    if not unlock_type:
        await message.err(r"I Can't Unlock Nothing! (－‸ლ)")
        return
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
                "**🔓 Unlocked all permission from this Chat!**", del_in=5)
            await CHANNEL.log(
                f"#UNLOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"PERMISSIONS: `All Permissions`")
        except Exception as e_f:
            await message.edit(
                r"`i don't have permission to do that ＞︿＜`\n\n"
                f"**ERROR:** `{e_f}`", del_in=5)
        return
    if unlock_type in _types:
        (umsg, umedia, ustickers,
         uanimations, ugames, uinlinebots,
         uwebprev, upolls, uinfo, uinvite,
         upin, uperm) = _get_chat_lock(message, unlock_type, False)
    else:
        await message.err(r"Invalid Unlock Type! ¯\_(ツ)_/¯")
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
        await message.edit(f"**🔓 Unlocked {uperm} for this chat!**", del_in=5)
        await CHANNEL.log(
            f"#UNLOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{uperm} Permission`")
    except Exception as e_f:
        await message.edit(
            r"`i don't have permission to do that ＞︿＜`\n\n"
            f"**ERROR:** `{e_f}`", del_in=5)


@userge.on_cmd("vperm", about={
    'header': "use this to view group permissions",
    'description': "Allows you to view permission types on/off status in the chat."},
    allow_channels=False, allow_bots=False, allow_private=False)
async def view_perm(message: Message):
    """ check chat permissions from tg group """
    await message.edit("`Checking group permissions... Hang on!! ⏳`")

    def convert_to_emoji(val: bool):
        return "✅" if val else "❌"
    vmsg = convert_to_emoji(message.chat.permissions.can_send_messages)
    vmedia = convert_to_emoji(message.chat.permissions.can_send_media_messages)
    vstickers = convert_to_emoji(message.chat.permissions.can_send_stickers)
    vanimations = convert_to_emoji(message.chat.permissions.can_send_animations)
    vgames = convert_to_emoji(message.chat.permissions.can_send_games)
    vinlinebots = convert_to_emoji(message.chat.permissions.can_use_inline_bots)
    vwebprev = convert_to_emoji(message.chat.permissions.can_add_web_page_previews)
    vpolls = convert_to_emoji(message.chat.permissions.can_send_polls)
    vinfo = convert_to_emoji(message.chat.permissions.can_change_info)
    vinvite = convert_to_emoji(message.chat.permissions.can_invite_users)
    vpin = convert_to_emoji(message.chat.permissions.can_pin_messages)
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
    if message.chat.photo and vmedia == "✅":
        local_chat_photo = await message.client.download_media(
            message=message.chat.photo.big_file_id)
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
