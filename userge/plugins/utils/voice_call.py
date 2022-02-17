""" Userge Voice-Call Plugin """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved
#
# Author (C) - @Krishna_Singhal (https://github.com/Krishna-Singhal)

import os
import re
import json
import shlex
import shutil
import asyncio
import requests
from pathlib import Path
from traceback import format_exc
from typing import List, Tuple, Optional
from json.decoder import JSONDecodeError
from youtubesearchpython import VideosSearch

from pyrogram import ContinuePropagation
from pyrogram.raw import functions
from pyrogram.raw.base import Message as BaseMessage
from pyrogram.raw.functions.phone import GetGroupCall
from pyrogram.raw.types import UpdateGroupCallParticipants, InputGroupCall, GroupCall
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message as RawMessage)

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    NodeJSNotInstalled,
    TooOldNodeJSVersion,
    NoActiveGroupCall,
    AlreadyJoinedError,
    NotInGroupCallError,
    GroupCallNotFound
)
from pytgcalls.types import (
    Update,
    StreamAudioEnded,
    JoinedGroupCallParticipant,
    LeftGroupCallParticipant
)
from pytgcalls.types.input_stream import (
    AudioVideoPiped,
    AudioPiped,
    VideoParameters
)

from userge import userge, Message, pool, filters, get_collection, Config
from userge.utils import time_formatter, import_ytdl, progress, runcmd, is_url
from userge.utils.exceptions import StopConversation

# https://github.com/pytgcalls/pytgcalls/blob/master/pytgcalls/mtproto/mtproto_client.py#L18
userge.__class__.__module__ = 'pyrogram.client'
call = PyTgCalls(userge, overload_quiet_mode=True)
call._env_checker.check_environment()  # pylint: disable=protected-access


CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger()

VC_DB = get_collection("VC_CMDS_TOGGLE")
CMDS_FOR_ALL = False
GROUP_CALL_PARTICIPANTS: List[int] = []

ADMINS = {}

PLAYING = False

CHAT_NAME = ""
CHAT_ID = 0
CONTROL_CHAT_IDS: List[int] = []
QUEUE: List[Message] = []
CLIENT = userge

BACK_BUTTON_TEXT = ""
CQ_MSG: List[RawMessage] = []

ytdl = import_ytdl()

yt_regex = re.compile(
    r'(https?://)?(www\.)?'
    r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
    r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%?]{11})'
)
_SCHEDULED = "[{title}]({link}) Scheduled to QUEUE on #{position} position"


async def _init():
    global CMDS_FOR_ALL  # pylint: disable=global-statement
    data = await VC_DB.find_one({'_id': 'VC_CMD_TOGGLE'})
    if data:
        CMDS_FOR_ALL = bool(data['is_enable'])


async def reply_text(
    msg: Message,
    text: str,
    markup=None,
    to_reply: bool = True,
    parse_mode: str = None,
    del_in: int = -1
) -> Message:
    kwargs = {
        'chat_id': msg.chat.id,
        'text': text,
        'del_in': del_in,
        'reply_to_message_id': msg.message_id if to_reply else None,
        'reply_markup': markup,
        'disable_web_page_preview': True
    }
    if parse_mode:
        kwargs['parse_mode'] = parse_mode
    new_msg = await msg.client.send_message(**kwargs)
    if to_reply and not isinstance(new_msg, bool):
        new_msg.reply_to_message = msg
    return new_msg


def _get_scheduled_text(title: str, link: str = None) -> str:
    return _SCHEDULED.format(title=title, link=link, position=len(QUEUE) + 1)


def vc_chat(func):
    """ decorator for Voice-Call chat """

    async def checker(msg: Message):
        if CHAT_ID and msg.chat.id in ([CHAT_ID] + CONTROL_CHAT_IDS):
            await func(msg)
        elif CHAT_ID and msg.outgoing:
            await msg.edit("You can't access voice_call from this chat.")
        elif msg.outgoing:
            await msg.edit("`Haven't join any Voice-Call...`")

    checker.__doc__ = func.__doc__

    return checker


def check_enable_for_all(func):
    """ decorator to check cmd is_enable for others """

    async def checker(msg: Message):
        is_self = msg.from_user and msg.from_user.id == userge.id
        user_in_vc = msg.from_user and msg.from_user.id in GROUP_CALL_PARTICIPANTS
        sender_chat_in_vc = msg.sender_chat and msg.sender_chat.id in GROUP_CALL_PARTICIPANTS

        if (is_self or (CMDS_FOR_ALL and ((user_in_vc) or (sender_chat_in_vc)))):
            await func(msg)

    checker.__doc__ = func.__doc__

    return checker


def check_cq_for_all(func):
    """ decorator to check CallbackQuery users """

    async def checker(_, cq: CallbackQuery):
        is_self = cq.from_user and cq.from_user.id == userge.id
        user_in_vc = cq.from_user and cq.from_user.id in GROUP_CALL_PARTICIPANTS

        if (is_self or (CMDS_FOR_ALL and user_in_vc)):
            await func(cq)
        else:
            await cq.answer(
                "⚠️ You don't have permission to use me", show_alert=True)

    checker.__doc__ = func.__doc__

    return checker


def default_markup():
    """ default markup for playing text """

    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(text="⏩ Skip", callback_data="skip"),
            InlineKeyboardButton(text="🗒 Queue", callback_data="queue")
        ]]
    )


def volume_button_markup():
    """ volume buttons markup """

    buttons = [
        [
            InlineKeyboardButton(text="🔈 50", callback_data="vol(50)"),
            InlineKeyboardButton(text="🔉 100", callback_data="vol(100)")
        ],
        [
            InlineKeyboardButton(text="🔉 150", callback_data="vol(150)"),
            InlineKeyboardButton(text="🔊 200", callback_data="vol(200)")
        ],
        [
            InlineKeyboardButton(text="🖌 Enter Manually", callback_data="vol(custom)"),
        ]
    ]

    return InlineKeyboardMarkup(buttons)


@userge.on_cmd("joinvc", about={
    'header': "Join Voice-Call",
    'flags': {
        '-as': "Join as any of your public channel.",
        '-at': "Joins vc in a remote chat and control it from saved messages/linked chat"},
    'examples': [
        "{tr}joinvc -as=@TheUserge -at=@UsergeOT - Join VC of @UsergeOT as @TheUserge.",
        "{tr}joinvc -at=-100123456789 - Join VC of any private channel / group."]},
    allow_bots=False)
async def joinvc(msg: Message):
    """ join voice chat """
    global CHAT_NAME, CHAT_ID, CONTROL_CHAT_IDS  # pylint: disable=global-statement

    await msg.delete()

    if CHAT_NAME:
        return await reply_text(msg, f"`Already joined in {CHAT_NAME}`")

    flags = msg.flags
    join_as = flags.get('-as')
    chat = flags.get('-at')

    if not chat and msg.chat.type == "private":
        return await msg.err("Invalid chat, either use in group / channel or use -at flag.")
    if chat:
        if chat.strip("-").isnumeric():
            chat = int(chat)
        try:
            _chat = await userge.get_chat(chat)
        except Exception as e:
            return await reply_text(msg, f'Invalid Join In Chat Specified\n{e}')
        CHAT_ID = _chat.id
        CHAT_NAME = _chat.title
        # Joins Voice_call in a remote chat and control it from Saved Messages
        # / Linked Chat
        CONTROL_CHAT_IDS.append(userge.id)
        if _chat.linked_chat:
            CONTROL_CHAT_IDS.append(_chat.linked_chat.id)
    else:
        CHAT_ID = msg.chat.id
        CHAT_NAME = msg.chat.title
    if join_as:
        if join_as.strip("-").isnumeric():
            join_as = int(join_as)
        try:
            join_as = (await userge.get_chat(join_as)).id
        except Exception as e:
            CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
            return await reply_text(msg, f'Invalid Join As Chat Specified\n{e}')
        join_as_peers = await userge.send(functions.phone.GetGroupCallJoinAs(
            peer=(
                await userge.resolve_peer(CHAT_ID)
            )
        ))
        raw_id = int(str(join_as).replace("-100", ""))
        if raw_id not in [
            getattr(peers, "user_id", None)
            or getattr(peers, "channel_id", None)
            for peers in join_as_peers.peers
        ]:
            CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
            return await reply_text(msg, "You cant join the voice chat as this channel.")

    if join_as:
        peer = await userge.resolve_peer(join_as)
    else:
        peer = await userge.resolve_peer(userge.id)
    try:
        # Initialising NodeJS
        if not call.is_connected:
            await call.start()
        # Joining with a dummy audio, since py-tgcalls wont allow joining
        # without file.
        await call.join_group_call(
            CHAT_ID,
            AudioPiped(
                'http://duramecho.com/Misc/SilentCd/Silence01s.mp3'
            ),
            join_as=peer,
            stream_type=StreamType().pulse_stream
        )
    except NoActiveGroupCall:
        try:
            peer = await userge.resolve_peer(CHAT_ID)
            await userge.send(
                functions.phone.CreateGroupCall(
                    peer=peer, random_id=2
                )
            )
            await asyncio.sleep(3)
            CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
            return await joinvc(msg)
        except Exception as err:
            CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
            return await reply_text(msg, err)
    except (NodeJSNotInstalled, TooOldNodeJSVersion):
        return await reply_text(msg, "NodeJs is not installed or installed version is too old.")
    except AlreadyJoinedError:
        await call.leave_group_call(CHAT_ID)
        await asyncio.sleep(3)
        CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
        return await joinvc(msg)
    except Exception as e:
        CHAT_ID, CHAT_NAME, CONTROL_CHAT_IDS = 0, '', []
        return await reply_text(msg, f'Error during Joining the Call\n`{e}`')

    await _on_join()
    await reply_text(msg, "`Joined VoiceChat Succesfully`", del_in=5)


@userge.on_cmd("leavevc", about={
    'header': "Leave Voice-Call",
    'usage': "{tr}leavevc"})
async def leavevc(msg: Message):
    """ leave voice chat """
    await msg.delete()
    if CHAT_NAME:
        try:
            await call.leave_group_call(CHAT_ID)
        except (NotInGroupCallError, NoActiveGroupCall):
            pass
        await _on_left()
        await reply_text(msg, "`Left Voicechat`", del_in=5)
    else:
        await reply_text(msg, "`I didn't find any Voice-Chat to leave")


@userge.on_cmd("vcmode", about={
    'header': "Toggle to enable or disable play and queue commands for all users"})
async def toggle_vc(msg: Message):
    """ toggle enable/disable vc cmds """

    global CMDS_FOR_ALL  # pylint: disable=global-statement

    await msg.delete()
    CMDS_FOR_ALL = not CMDS_FOR_ALL

    await VC_DB.update_one(
        {'_id': 'VC_CMD_TOGGLE'},
        {"$set": {'is_enable': CMDS_FOR_ALL}},
        upsert=True
    )

    text = (
        "**Enabled**" if CMDS_FOR_ALL else "**Disabled**"
    ) + " commands Successfully"

    await reply_text(msg, text, del_in=5)


@userge.on_cmd("play", about={
    'header': "play or add songs to queue",
    'flags': {
        '-v': "Stream as video.",
        '-q': "Quality of video stream (1-100)"}},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@check_enable_for_all
@vc_chat
async def _play(msg: Message):
    """ play music in voice call """
    return await play_music(msg, False)


@userge.on_cmd("forceplay", about={
    'header': "Force play with skip the current song and "
              "Play your song on #1 Position",
    'flags': {
        '-v': "Stream as video.",
        '-q': "Quality of video stream (1-100)"}})
@vc_chat
async def _forceplay(msg: Message):
    """ forceplay music in voice call """
    return await play_music(msg, True)


async def play_music(msg: Message, forceplay: bool):
    """ play music """
    global CLIENT  # pylint: disable=global-statement

    input_str = msg.filtered_input_str
    flags = msg.flags
    is_video = "-v" in flags
    path = Path(input_str)
    quality = flags.get('-q', 80)
    if input_str:
        if yt_regex.match(input_str):
            details = await _get_song_info(input_str)
            if not details:
                return await reply_text(msg, "**ERROR:** `Max song duration limit reached!`")
            name, duration = details
            if PLAYING and not forceplay:
                msg = await reply_text(msg, _get_scheduled_text(name, input_str))
            else:
                msg = await reply_text(msg, f"[{name}]({input_str})")
            flags["duration"] = duration
            setattr(msg, '_flags', flags)
            if forceplay:
                QUEUE.insert(0, msg)
            else:
                QUEUE.append(msg)
        elif (is_url(input_str) or (path.exists() and path.is_file())):
            if path.exists():
                if not path.name.endswith(
                    (".mkv", ".mp4", ".webm", ".m4v", ".mp3", ".flac", ".wav", ".m4a")
                ):
                    return await reply_text(msg, "`invalid file path provided to stream!`")
                path_to_media = str(path.absolute())
                filename = path.name
            else:
                try:
                    res = await pool.run_in_thread(
                        requests.get
                    )(input_str, allow_redirects=True, stream=True)
                    headers = dict(res.headers)
                    if (
                        "video" not in headers["Content-Type"]
                        and "audio" not in headers["Content-Type"]
                    ):
                        raise Exception
                    path_to_media = input_str
                    filename = headers["Content-Disposition"].split('=', 1)[1].strip('"')
                except Exception:
                    return await reply_text(msg, "`invalid direct link provided to stream!`")
            setattr(msg, 'path_to_media', path_to_media)
            setattr(msg, 'file_name', filename.replace('_', ' '))
            setattr(msg, 'is_video', is_video)
            setattr(msg, 'quality', quality)
            CLIENT = msg.client
            if forceplay:
                QUEUE.insert(0, msg)
            else:
                if PLAYING:
                    await reply_text(msg, _get_scheduled_text(msg.file_name))
                QUEUE.append(msg)
        else:
            mesg = await reply_text(msg, f"Searching `{input_str}` on YouTube")
            title, link = await _get_song(input_str)
            if link:
                details = await _get_song_info(link)
                if not details:
                    return await mesg.edit("Invalid YouTube link found during search!")
                _, duration = details
                if PLAYING and not forceplay:
                    msg = await reply_text(msg, _get_scheduled_text(title, link))
                else:
                    msg = await msg.edit(f"[{title}]({link})")
                flags["duration"] = duration
                await mesg.delete()
                setattr(msg, '_flags', flags)
                if forceplay:
                    QUEUE.insert(0, msg)
                else:
                    QUEUE.append(msg)
            else:
                await mesg.edit("No results found.")
    elif msg.reply_to_message:
        replied = msg.reply_to_message
        replied_file = replied.audio or replied.video or replied.document
        if not replied_file:
            return await reply_text(msg, "Input not found")
        if replied.audio:
            setattr(
                replied.audio,
                'file_name',
                replied_file.title or replied_file.file_name or "Song")
            setattr(replied.audio, 'is_video', False)
            setattr(replied.audio, 'quality', 100)
        elif replied.video:
            setattr(replied.video, 'is_video', is_video)
            setattr(replied.video, 'quality', quality)
        elif replied.document and "video" in replied.document.mime_type:
            setattr(replied.document, 'is_video', is_video)
            setattr(replied.document, 'quality', quality)
        else:
            return await reply_text(msg, "Replied media is invalid.")

        CLIENT = msg.client
        if forceplay:
            QUEUE.insert(0, replied)
        else:
            if PLAYING:
                await reply_text(msg, _get_scheduled_text(replied_file.file_name, replied.link))
            QUEUE.append(replied)
    else:
        return await reply_text(msg, "Input not found")

    if not PLAYING or forceplay:
        await _skip()


@userge.on_cmd("helpvc",
               about={'header': "help for voice_call plugin"},
               trigger=Config.PUBLIC_TRIGGER,
               allow_private=False,
               check_client=True,
               filter_me=False,
               allow_bots=False)
@vc_chat
@check_enable_for_all
async def _help(msg: Message):
    """ help commands of this plugin for others """

    commands = userge.manager.enabled_plugins["voice_call"].enabled_commands
    key = msg.input_str.lstrip(Config.PUBLIC_TRIGGER)
    cmds = []
    raw_cmds = []

    for i in commands:
        if i.name.startswith(Config.PUBLIC_TRIGGER):
            cmds.append(i)
            raw_cmds.append(i.name)

    if not key:
        out_str = f"""⚔ <b><u>(<code>{len(cmds)}</code>) Command(s) Available</u></b>

🔧 <b>Plugin:</b>  <code>voice_call</code>
📘 <b>Doc:</b>  <code>Userge Voice-Call Plugin</code>\n\n"""
        for i, cmd in enumerate(cmds, start=1):
            out_str += (
                f"    🤖 <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                f"    📚 <b>info:</b>  <i>{cmd.doc}</i>\n\n")
        return await reply_text(msg, out_str, parse_mode="html")

    key = Config.PUBLIC_TRIGGER + key
    if key in raw_cmds:
        for cmd in cmds:
            if cmd.name == key:
                out_str = f"<code>{key}</code>\n\n{cmd.about}"
                await reply_text(msg, out_str, parse_mode="html")
                break


@userge.on_cmd("current", about={
    'header': "View Current playing Song.",
    'usage': "{tr}current"},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@vc_chat
@check_enable_for_all
async def current(msg: Message):
    """ View current playing song """

    if not BACK_BUTTON_TEXT:
        return await reply_text(msg, "No song is playing!")
    await reply_text(
        msg,
        BACK_BUTTON_TEXT,
        markup=default_markup() if userge.has_bot else None,
        to_reply=True
    )


@userge.on_cmd("queue", about={
    'header': "View Queue of Songs",
    'usage': "{tr}queue"},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@vc_chat
@check_enable_for_all
async def view_queue(msg: Message):
    """ View Queue """

    if not QUEUE:
        out = "`Queue is empty`"
    else:
        out = f"**{len(QUEUE)} Songs in Queue:**\n"
        for i, m in enumerate(QUEUE, start=1):
            file = m.audio or m.video or m.document or None
            if hasattr(m, 'file_name'):
                out += f"\n{i}. {m.file_name}"
            elif file:
                out += f"\n{i}. [{file.file_name}]({m.link})"
            else:
                title, link = _get_yt_info(m)
                out += f"\n{i}. [{title}]({link})"

    await reply_text(msg, out)


@userge.on_cmd("volume", about={
    'header': "Set volume",
    'usage': "{tr}volume\n{tr}volume 69"})
@vc_chat
async def set_volume(msg: Message):
    """ change volume """

    await msg.delete()

    if msg.input_str:
        if msg.input_str.isnumeric():
            if 200 >= int(msg.input_str) > 0:
                await call.change_volume_call(CHAT_ID, int(msg.input_str))
                await reply_text(msg, f"Successfully set volume to __{msg.input_str}__")
            else:
                await reply_text(msg, "Invalid Range!")
        else:
            await reply_text(msg, "Invalid Arguments!")
    else:
        try:
            await userge.bot.send_message(
                msg.chat.id,
                "**🎚 Volume Control**\n\n`Click on the button to change volume"
                " or Click last option to Enter volume manually.`",
                reply_markup=volume_button_markup()
            )
        except Exception:
            await reply_text(msg, "Input not found!")


@userge.on_cmd("skip", about={
    'header': "Skip Song",
    'usage': "{tr}skip\n{tr}skip 2"},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@vc_chat
async def skip_music(msg: Message):
    """ skip music in vc """
    await msg.delete()
    if not QUEUE and not PLAYING:
        return
    if (
        msg.input_str
        and msg.input_str.isnumeric()
        and (len(QUEUE) >= int(msg.input_str) > 0)
    ):
        m = QUEUE.pop(int(msg.input_str) - 1)
        file = m.audio or m.video or m.document or None
        if hasattr(m, 'file_name'):
            out = f"`Skipped` {m.file_name}"
        elif file:
            out = f"`Skipped` [{file.file_name}]({m.link})"
        else:
            title, link = _get_yt_info(m)
            out = f"`Skipped` [{title}]({link})"
        await reply_text(msg, out)
        return
    await reply_text(msg, "`Skipped`")
    await _skip()


@userge.on_cmd("pause", about={
    'header': "Pause Song.",
    'usage': "{tr}pause"},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@vc_chat
async def pause_music(msg: Message):
    """ pause music in vc """
    await msg.delete()
    await call.pause_stream(CHAT_ID)
    await reply_text(msg, "⏸️ **Paused** Music Successfully")


@userge.on_cmd("resume", about={
    'header': "Resume Song.",
    'usage': "{tr}resume"},
    trigger=Config.PUBLIC_TRIGGER, check_client=True,
    filter_me=False, allow_bots=False)
@vc_chat
async def resume_music(msg: Message):
    """ resume music in vc """
    await msg.delete()
    await call.resume_stream(CHAT_ID)
    await reply_text(msg, "◀️ **Resumed** Music Successfully")


@userge.on_cmd("stopvc", about={
    'header': "Stop vc and clear Queue.",
    'usage': "{tr}stopvc"})
@vc_chat
async def stop_music(msg: Message):
    """ stop music in vc """
    await msg.delete()
    await _skip(True)
    await reply_text(msg, "`Stopped Userge-Music.`", del_in=5)


@userge.on_raw_update()
async def _on_raw(_, m: BaseMessage, *__) -> None:
    if isinstance(m, UpdateGroupCallParticipants):
        # TODO: chat_id
        for participant in m.participants:
            if participant.is_self:
                group_call = await userge.send(
                    GetGroupCall(call=InputGroupCall(
                        access_hash=m.call.access_hash,
                        id=m.call.id), limit=1)
                )
                if participant.just_joined:
                    await _on_join(group_call.call)
                elif participant.left:
                    await _on_left(group_call.call)
                break
    raise ContinuePropagation


async def _on_join(group_call: Optional[GroupCall] = None) -> None:
    if group_call:
        LOG.info("Joined group call: [%s], participants: [%s]",
                 group_call.title, group_call.participants_count)
    else:
        LOG.info("Joined group call: [%s] [joinvc]", CHAT_NAME)
        try:
            GROUP_CALL_PARTICIPANTS.clear()
            for p in await call.get_participants(CHAT_ID):
                if p.user_id == userge.id:
                    continue
                GROUP_CALL_PARTICIPANTS.append(p.user_id)
        except GroupCallNotFound as err:
            LOG.error(err)


async def _on_left(group_call: Optional[GroupCall] = None) -> None:
    global CHAT_NAME, CHAT_ID, PLAYING, BACK_BUTTON_TEXT  # pylint: disable=global-statement

    if group_call:
        LOG.info("Left group call: [%s], participants: [%s]",
                 group_call.title, group_call.participants_count)
    else:
        LOG.info("Left group call: [%s] [leavevc]", CHAT_NAME)

    CHAT_NAME = ""
    CHAT_ID = 0
    CONTROL_CHAT_IDS.clear()
    QUEUE.clear()
    GROUP_CALL_PARTICIPANTS.clear()
    PLAYING = False
    BACK_BUTTON_TEXT = ""
    if CQ_MSG:
        for msg in CQ_MSG:
            await msg.delete()
        CQ_MSG.clear()


@call.on_stream_end()
async def _stream_end_handler(_: PyTgCalls, update: Update):
    if isinstance(update, StreamAudioEnded):
        await _skip()


@call.on_participants_change()
async def _participants_change_handler(_: PyTgCalls, update: Update):
    if isinstance(update, JoinedGroupCallParticipant):
        GROUP_CALL_PARTICIPANTS.append(update.participant.user_id)
    elif isinstance(update, LeftGroupCallParticipant):
        GROUP_CALL_PARTICIPANTS.remove(update.participant.user_id)


async def _skip(clear_queue: bool = False):
    global PLAYING  # pylint: disable=global-statement

    if PLAYING:
        # skip current playing song the play next
        await call.change_stream(
            CHAT_ID,
            AudioPiped(
                'http://duramecho.com/Misc/SilentCd/Silence01s.mp3'
            )
        )
    PLAYING = True

    if CQ_MSG:
        for msg in CQ_MSG:
            await msg.delete()
        CQ_MSG.clear()

    if clear_queue:
        QUEUE.clear()

    if not QUEUE:
        PLAYING = False
        return

    shutil.rmtree("temp_music_dir", ignore_errors=True)
    msg = QUEUE.pop(0)

    try:
        if msg.audio or msg.video or msg.document or hasattr(msg, "file_name"):
            await tg_down(msg)
        else:
            await yt_down(msg)
    except Exception as err:
        PLAYING = False
        out = f'**ERROR:** `{err}`'
        await CHANNEL.log(f"`{format_exc().strip()}`")
        if QUEUE:
            out += "\n\n`Playing next Song.`"
        await CLIENT.send_message(
            CHAT_ID,
            out,
            disable_web_page_preview=True
        )
        await _skip()


async def yt_down(msg: Message):
    """ youtube downloader """

    global BACK_BUTTON_TEXT  # pylint: disable=global-statement

    title, url = _get_yt_info(msg)
    message = await reply_text(msg, f"`Preparing {title}`")
    stream_link = await get_stream_link(url)

    if not stream_link:
        raise Exception("Song not Downloaded, add again in Queue [your wish]")

    flags = msg.flags
    is_video = "-v" in flags
    duration = flags.get("duration")
    quality = max(min(100, int(flags.get('-q', 100))), 1)
    height, width, has_audio, has_video = await get_file_info(stream_link)

    if is_video and has_video:
        await play_video(stream_link, height, width, quality)
    elif has_audio:
        await play_audio(stream_link)
    else:
        out = "Invalid media found in queue, and skipped"
        if QUEUE:
            out += "\n\n`Playing next Song.`"
        await reply_text(
            msg,
            out
        )
        return await _skip()

    await message.delete()

    BACK_BUTTON_TEXT = (
        f"🎶 **Now playing:** [{title}]({url})\n"
        f"⏳ **Duration:** `{duration}`\n"
        f"🎧 **Requested By:** {requester(msg)}"
    )

    raw_msg = await reply_text(
        msg,
        BACK_BUTTON_TEXT,
        markup=default_markup() if userge.has_bot else None,
        to_reply=False
    )
    CQ_MSG.append(raw_msg)

    if msg.from_user and msg.client.id == msg.from_user.id:
        await msg.delete()


async def tg_down(msg: Message):
    """ TG downloader """

    global BACK_BUTTON_TEXT  # pylint: disable=global-statement

    file = msg.audio or msg.video or msg.document or msg
    title = file.file_name
    setattr(msg, '_client', CLIENT)
    message = await reply_text(
        msg, f"`{'Preparing' if hasattr(msg, 'file_name') else 'Downloading'} {title}`"
    )
    if not hasattr(msg, "path_to_media"):
        path = await msg.client.download_media(
            message=msg,
            file_name="temp_music_dir/",
            progress=progress,
            progress_args=(message, "Downloading..."))
        filename = os.path.join("temp_music_dir", os.path.basename(path))
        if msg.audio:
            duration = msg.audio.duration
        elif msg.video or msg.document:
            duration = await get_duration(shlex.quote(filename))
    else:
        filename = msg.path_to_media
        duration = await get_duration(shlex.quote(msg.path_to_media))
    if duration > Config.MAX_DURATION:
        await reply_text(msg, "**ERROR:** `Max song duration limit reached!`")
        return await _skip()

    height, width, has_audio, has_video = await get_file_info(shlex.quote(filename))

    is_video = file.is_video
    quality = max(min(100, int(getattr(file, 'quality', 100))), 1)

    if is_video and has_video:
        await play_video(filename, height, width, quality)
    elif has_audio:
        await play_audio(filename)
    else:
        out = "Invalid media found in queue, and skipped"
        if QUEUE:
            out += "\n\n`Playing next Song.`"
        await reply_text(
            msg,
            out
        )
        return await _skip()

    await message.delete()

    BACK_BUTTON_TEXT = (
        f"🎶 **Now playing:** [{title}]({msg.link if not hasattr(msg, 'file_name') else None})\n"
        f"⏳ **Duration:** `{time_formatter(duration)}`\n"
        f"🎧 **Requested By:** {requester(msg)}"
    )

    raw_msg = await reply_text(
        msg,
        BACK_BUTTON_TEXT,
        markup=default_markup() if userge.has_bot else None,
        to_reply=False
    )
    CQ_MSG.append(raw_msg)


async def play_video(file: str, height: int, width: int, quality: int):
    r_width, r_height = get_quality_ratios(width, height, quality)
    try:
        await call.change_stream(
            CHAT_ID,
            AudioVideoPiped(
                file,
                video_parameters=VideoParameters(
                    r_width,
                    r_height,
                    25
                )
            )
        )
    except NotInGroupCallError:
        await call.join_group_call(
            CHAT_ID,
            AudioVideoPiped(
                file,
                video_parameters=VideoParameters(
                    r_width,
                    r_height,
                    25
                )
            )
        )


async def play_audio(file: str):
    try:
        await call.change_stream(
            CHAT_ID,
            AudioPiped(
                file
            )
        )
    except NotInGroupCallError:
        await call.join_group_call(
            CHAT_ID,
            AudioPiped(
                file
            ),
            stream_type=StreamType().pulse_stream,
        )


async def get_stream_link(link: str) -> str:
    yt_dl = (os.environ.get("YOUTUBE_DL_PATH", "youtube_dl")).replace("_", "-")
    cmd = yt_dl + \
        " --geo-bypass -g -f best[height<=?720][width<=?1280]/best " + link
    out, err, _, _ = await runcmd(cmd)
    if err:
        return False
    return out


async def get_duration(file: str) -> int:
    dur = 0
    cmd = "ffprobe -i {file} -v error -show_entries format=duration -of json -select_streams v:0"
    out, _, _, _ = await runcmd(cmd.format(file=file))
    try:
        out = json.loads(out)
    except JSONDecodeError:
        dur = 0
    dur = int(float((out.get("format", {})).get("duration", 0)))
    return dur


async def get_file_info(file) -> Tuple[int, int, bool, bool]:
    cmd = "ffprobe -v error -show_entries stream=width,height,codec_type,codec_name -of json {file}"
    out, _, _, _ = await runcmd(cmd.format(file=file))
    try:
        output = json.loads(out) or {}
    except JSONDecodeError:
        output = {}
    streams = output.get('streams', [])
    width, height, have_audio, have_video = 0, 0, False, False
    for stream in streams:
        if (
            stream.get('codec_type', '') == 'video'
            and stream.get('codec_name', '') not in ['png', 'jpeg', 'jpg']
        ):
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
            if width and height:
                have_video = True
        elif stream.get('codec_type', '') == "audio":
            have_audio = True
    return height, width, have_audio, have_video


def requester(msg: Message):
    if not msg.from_user:
        if msg.sender_chat:
            return msg.sender_chat.title
        return None
    replied = msg.reply_to_message
    if replied and msg.client.id == msg.from_user.id:
        if not replied.from_user:
            if replied.sender_chat:
                return replied.sender_chat.title
            return None
        return replied.from_user.mention
    return msg.from_user.mention


def _get_yt_info(msg: Message) -> Tuple[str, str]:
    if msg.entities:
        for e in msg.entities:
            if e.url:
                return msg.text[e.offset:e.length], e.url
    return "", ""


def get_quality_ratios(w: int, h: int, q: int) -> Tuple[int, int]:
    rescaling = min(w, 1280) * 100 / w if w > h else min(h, 720) * 100 / h
    h = round((h * rescaling) / 100 * (q / 100))
    w = round((w * rescaling) / 100 * (q / 100))
    return w - 1 if w % 2 else w, h - 1 if h % 2 else h


@pool.run_in_thread
def _get_song(name: str) -> Tuple[str, str]:
    results: List[dict] = VideosSearch(name, limit=1).result()['result']
    if results:
        return results[0].get('title', name), results[0].get('link')
    return name, ""


@pool.run_in_thread
def _get_song_info(url: str):
    ydl_opts = {}

    with ytdl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = info.get("duration") or 0

        if duration > Config.MAX_DURATION:
            return False
    return info.get("title"), time_formatter(duration) if duration else "Live"


if userge.has_bot:
    @userge.bot.on_callback_query(filters.regex("(skip|queue|back)"))
    @check_cq_for_all
    async def vc_callback(cq: CallbackQuery):
        if not CHAT_NAME:
            await cq.edit_message_text("`Already Left Voice-Call`")
            return

        if "skip" in cq.data:
            text = f"{cq.from_user.mention} Skipped the Song."
            pattern = re.compile(r'\[(.*)\]')
            name = None
            for match in pattern.finditer(BACK_BUTTON_TEXT):
                name = match.group(1)
                break
            if name:
                text = f"{cq.from_user.mention} Skipped `{name}`."

            if CQ_MSG:
                for i, msg in enumerate(CQ_MSG):
                    if msg.message_id == cq.message.message_id:
                        CQ_MSG.pop(i)
                        break

            await cq.edit_message_text(text, disable_web_page_preview=True)
            await _skip()

        elif "queue" in cq.data:
            if not QUEUE:
                out = "`Queue is empty.`"
            else:
                out = f"**{len(QUEUE)} Song"
                out += f"{'s' if len(QUEUE) > 1 else ''} in Queue:**\n"
                for i, m in enumerate(QUEUE, start=1):
                    file = m.audio or m.video or m.document or None
                    if hasattr(m, 'file_name'):
                        out = f"\n{i}. {m.file_name}"
                    elif file:
                        out += f"\n{i}. [{file.file_name}]({m.link})"
                    else:
                        title, link = _get_yt_info(m)
                        out += f"\n{i}. [{title}]({link})"

            out += f"\n\n**Clicked by:** {cq.from_user.mention}"
            button = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="back")]]
            )

            await cq.edit_message_text(
                out,
                disable_web_page_preview=True,
                reply_markup=button
            )

        elif "back" in cq.data:
            if BACK_BUTTON_TEXT:
                await cq.edit_message_text(
                    BACK_BUTTON_TEXT,
                    disable_web_page_preview=True,
                    reply_markup=default_markup()
                )
            else:
                await cq.message.delete()

    @userge.bot.on_callback_query(filters.regex(r"vol\((.+)\)"))
    @check_cq_for_all
    async def vol_callback(cq: CallbackQuery):

        arg = cq.matches[0].group(1)
        volume = 0

        if arg.isnumeric():
            volume = int(arg)

        elif arg == "custom":

            try:
                async with userge.conversation(cq.message.chat.id, user_id=cq.from_user.id) as conv:
                    await cq.edit_message_text("`Now Input Volume`")

                    def _filter(_, __, m: RawMessage) -> bool:
                        r = m.reply_to_message
                        return r and r.message_id == cq.message.message_id

                    response = await conv.get_response(mark_read=True,
                                                       filters=filters.create(_filter))
            except StopConversation:
                await cq.edit_message_text("No arguments passed!")
                return

            if response.text.isnumeric():
                volume = int(response.text)
            else:
                await cq.edit_message_text("`Invalid Arguments!`")
                return

        if 200 >= volume > 0:
            await call.change_volume_call(CHAT_ID, volume)
            await cq.edit_message_text(f"Successfully set volume to {volume}")
        else:
            await cq.edit_message_text("`Invalid Range!`")
