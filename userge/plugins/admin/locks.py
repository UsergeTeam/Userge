""" set permissions to users """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
from typing import Tuple, Optional

from pyrogram.types import ChatPermissions
from pyrogram.errors import ChatNotModified
from pyrogram.raw.types import InputPeerChannel, ChatBannedRights
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat, EditChatDefaultBannedRights

from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)

_types = ('msg', 'media', 'polls', 'invite', 'pin', 'info', 'webprev',
          'inlinebots', 'animations', 'games', 'stickers')


async def _get_banned_rights(message: Message) -> ChatBannedRights:
    peer = await message.client.resolve_peer(message.chat.id)
    if isinstance(peer, InputPeerChannel):
        return (await message.client.send(
            GetFullChannel(
                channel=peer))).chats[0].default_banned_rights
    return (await message.client.send(
        GetFullChat(
            chat_id=peer.chat_id))).chats[0].default_banned_rights


async def _get_new_rights(message: Message, lock_type: str,
                          should_lock: bool) -> Tuple[ChatBannedRights, str]:
    ban_rights = await _get_banned_rights(message)
    ban_rights.until_date = 0
    perm = None

    if lock_type == "msg":
        ban_rights.send_messages = should_lock
        perm = "messages"
    elif lock_type == "media":
        ban_rights.send_media = should_lock
        perm = "audios, documents, photos, videos, video notes, voice notes"
    elif lock_type == "stickers":
        ban_rights.send_stickers = should_lock
        perm = "stickers"
    elif lock_type == "animations":
        ban_rights.send_gifs = should_lock
        perm = "animations"
    elif lock_type == "games":
        ban_rights.send_games = should_lock
        perm = "games"
    elif lock_type == "inlinebots":
        ban_rights.send_inline = should_lock
        perm = "inline bots"
    elif lock_type == "webprev":
        ban_rights.embed_links = should_lock
        perm = "web page previews"
    elif lock_type == "polls":
        ban_rights.send_polls = should_lock
        perm = "polls"
    elif lock_type == "info":
        ban_rights.change_info = should_lock
        perm = "info"
    elif lock_type == "invite":
        ban_rights.invite_users = should_lock
        perm = "invite"
    elif lock_type == "pin":
        ban_rights.pin_messages = should_lock
        perm = "pin"

    return ban_rights, perm


async def _edit_ban_rights(message: Message, rights: Optional[ChatBannedRights] = None) -> None:
    if rights is None:
        rights = ChatBannedRights(
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
            pin_messages=False)

    await message.client.send(
        EditChatDefaultBannedRights(
            peer=await message.client.resolve_peer(message.chat.id),
            banned_rights=rights))


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
        new_rights, perm = await _get_new_rights(message, lock_type, True)
    else:
        await message.err(r"Invalid lock type! ¯\_(ツ)_/¯")
        return
    try:
        await _edit_ban_rights(message, new_rights)
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
            await _edit_ban_rights(message)
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
        new_rights, perm = await _get_new_rights(message, unlock_type, False)
    else:
        await message.err(r"Invalid Unlock Type! ¯\_(ツ)_/¯")
        return
    try:
        await _edit_ban_rights(message, new_rights)
        await message.edit(f"**🔓 Unlocked {perm} for this chat!**", del_in=5)
        await CHANNEL.log(
            f"#UNLOCK\n\nCHAT: `{message.chat.title}` (`{chat_id}`)\n"
            f"PERMISSIONS: `{perm} Permission`")
    except ChatNotModified:
        await message.edit(f"Nothing was changed, since {perm} is not locked here.", del_in=5)
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
    ban_rights = await _get_banned_rights(message)

    permission_view_str = "<b>CHAT PERMISSION INFO:</b>\n\n"
    permission_view_str += f"<b>📩 Send Messages:</b> {_emojify(ban_rights.send_messages)}\n"
    permission_view_str += f"<b>🎭 Send Media:</b> {_emojify(ban_rights.send_media)}\n"
    permission_view_str += f"<b>🎴 Send Stickers:</b> {_emojify(ban_rights.send_stickers)}\n"
    permission_view_str += f"<b>🎲 Send Animations:</b> {_emojify(ban_rights.send_gifs)}\n"
    permission_view_str += f"<b>🎮 Can Play Games:</b> {_emojify(ban_rights.send_games)}\n"
    permission_view_str += f"<b>🤖 Can Use Inline Bots:</b> {_emojify(ban_rights.send_inline)}\n"
    permission_view_str += f"<b>🌐 Webpage Preview:</b> {_emojify(ban_rights.embed_links)}\n"
    permission_view_str += f"<b>🗳 Send Polls:</b> {_emojify(ban_rights.send_polls)}\n"
    permission_view_str += f"<b>ℹ Change Info:</b> {_emojify(ban_rights.change_info)}\n"
    permission_view_str += f"<b>👥 Invite Users:</b> {_emojify(ban_rights.invite_users)}\n"
    permission_view_str += f"<b>📌 Pin Messages:</b> {_emojify(ban_rights.pin_messages)}\n"

    if message.chat.photo and not ban_rights.send_media:
        local_chat_photo = await message.client.download_media(
            message=message.chat.photo.big_file_id)
        await message.client.send_photo(chat_id=message.chat.id,
                                        photo=local_chat_photo,
                                        caption=permission_view_str,
                                        parse_mode="html")
        os.remove(local_chat_photo)
        await message.delete()
    else:
        await message.edit(permission_view_str)

    await CHANNEL.log("`vperm` command executed")


def _emojify(banned: bool):
    return "❌" if banned else "✅"
