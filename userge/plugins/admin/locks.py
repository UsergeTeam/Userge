""" set permissions to users """

# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from typing import Sequence

from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatNotModified
from pyrogram.raw.types import InputPeerChannel, ChatBannedRights
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat, EditChatDefaultBannedRights

from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)

_types = [
    'msg', 'media', 'polls', 'invite', 'pin', 'info',
    'webprev', 'inlinebots', 'animations', 'games', 'stickers'
]


def _get_chat_lock(permissions: ChatBannedRights, lock_type: str,
                   should_lock: bool) -> Sequence[str]:
    lock = not should_lock
    msg = not permissions.send_messages
    media = not permissions.send_media
    stickers = not permissions.send_stickers
    animations = not permissions.send_gifs
    games = not permissions.send_games
    inlinebots = not permissions.send_inline
    webprev = not permissions.embed_links
    polls = not permissions.send_polls
    info = not permissions.change_info
    invite = not permissions.invite_users
    pin = not permissions.pin_messages
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
        peer = await message.client.resolve_peer(chat_id)
        if isinstance(peer, InputPeerChannel):
            chat_perm = (await message.client.send(
                GetFullChannel(
                    channel=peer))).chats[0].default_banned_rights
        else:
            chat_perm = (await message.client.send(
                GetFullChat(
                    chat_id=peer.chat_id))).chats[0].default_banned_rights
        (msg, media, stickers,
         animations, games, inlinebots,
         webprev, polls, info, invite,
         pin, perm) = _get_chat_lock(chat_perm, lock_type, True)
    else:
        await message.err(r"Invalid lock type! ¯\_(ツ)_/¯")
        return
    try:
        await message.client.send(
            EditChatDefaultBannedRights(
                peer=await message.client.resolve_peer(chat_id),
                banned_rights=ChatBannedRights(
                    until_date=0,
                    send_messages=True if not msg else None,
                    send_media=True if not media else None,
                    send_stickers=True if not stickers else None,
                    send_gifs=True if not animations else None,
                    send_games=True if not games else None,
                    send_inline=True if not inlinebots else None,
                    embed_links=True if not webprev else None,
                    send_polls=True if not polls else None,
                    change_info=True if not info else None,
                    invite_users=True if not invite else None,
                    pin_messages=True if not pin else None)))
        await message.edit(f"**🔒 Locked {perm} for this chat!**", del_in=5)
        await CHANNEL.log(
            f"#LOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{perm} Permission`")
    except ChatNotModified:
        await message.edit(f"Nothing was changed, since {perm} is already locked.", del_in=5)
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
            await message.client.send(
                EditChatDefaultBannedRights(
                    peer=await message.client.resolve_peer(chat_id),
                    banned_rights=ChatBannedRights(
                        until_date=0,
                        send_messages=False,
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        embed_links=False,
                        send_polls=False,
                        change_info=False,
                        invite_users=False,
                        pin_messages=False)))
            await message.edit(
                "**🔓 Unlocked all permission from this Chat!**", del_in=5)
            await CHANNEL.log(
                f"#UNLOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
                f"PERMISSIONS: `All Permissions`")
        except ChatNotModified:
            await message.edit(
                "Nothing was changed, since currently no locks are applied here.",
                del_in=5)
        except Exception as e_f:
            await message.edit(
                r"`i don't have permission to do that ＞︿＜`\n\n"
                f"**ERROR:** `{e_f}`", del_in=5)
        return
    if unlock_type in _types:
        peer = await message.client.resolve_peer(chat_id)
        if isinstance(peer, InputPeerChannel):
            chat_perm = (await message.client.send(
                GetFullChannel(
                    channel=peer))).chats[0].default_banned_rights
        else:
            chat_perm = (await message.client.send(
                GetFullChat(
                    chat_id=peer.chat_id))).chats[0].default_banned_rights
        (umsg, umedia, ustickers,
         uanimations, ugames, uinlinebots,
         uwebprev, upolls, uinfo, uinvite,
         upin, uperm) = _get_chat_lock(chat_perm, unlock_type, False)
    else:
        await message.err(r"Invalid Unlock Type! ¯\_(ツ)_/¯")
        return
    try:
        await message.client.send(
            EditChatDefaultBannedRights(
                peer=await message.client.resolve_peer(chat_id),
                banned_rights=ChatBannedRights(
                    until_date=0,
                    send_messages=True if not umsg else None,
                    send_media=True if not umedia else None,
                    send_stickers=True if not ustickers else None,
                    send_gifs=True if not uanimations else None,
                    send_games=True if not ugames else None,
                    send_inline=True if not uinlinebots else None,
                    embed_links=True if not uwebprev else None,
                    send_polls=True if not upolls else None,
                    change_info=True if not uinfo else None,
                    invite_users=True if not uinvite else None,
                    pin_messages=True if not upin else None)))
        await message.edit(f"**🔓 Unlocked {uperm} for this chat!**", del_in=5)
        await CHANNEL.log(
            f"#UNLOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{uperm} Permission`")
    except ChatNotModified:
        await message.edit(f"Nothing was changed, since {uperm} is not locked here.", del_in=5)
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
    peer = await message.client.resolve_peer(message.chat.id)
    if isinstance(peer, InputPeerChannel):
        chat_perm = (await message.client.send(
            GetFullChannel(
                channel=peer))).chats[0].default_banned_rights
    else:
        chat_perm = (await message.client.send(
            GetFullChat(
                chat_id=peer.chat_id))).chats[0].default_banned_rights
    (vmsg, vmedia, vstickers,
     vanimations, vgames, vinlinebots,
     vwebprev, vpolls, vinfo, vinvite,
     vpin, _) = _get_chat_lock(chat_perm, "_", False)

    def convert_to_emoji(val: bool):
        return "✅" if val else "❌"
    vmsg = convert_to_emoji(vmsg)
    vmedia = convert_to_emoji(vmedia)
    vstickers = convert_to_emoji(vstickers)
    vanimations = convert_to_emoji(vanimations)
    vgames = convert_to_emoji(vgames)
    vinlinebots = convert_to_emoji(vinlinebots)
    vwebprev = convert_to_emoji(vwebprev)
    vpolls = convert_to_emoji(vpolls)
    vinfo = convert_to_emoji(vinfo)
    vinvite = convert_to_emoji(vinvite)
    vpin = convert_to_emoji(vpin)
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
