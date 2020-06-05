# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import time
import base64
import asyncio

import aiofiles
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Message as RawMessage
from pyrogram.errors.exceptions import FileIdInvalid, FileReferenceEmpty
from pyrogram.errors.exceptions.bad_request_400 import BadRequest

from userge import userge, Filters, Message, Config, get_collection
from userge.utils import SafeDict, progress, take_screen_shot

THUMB_PATH = Config.DOWN_PATH + "thumb_image.jpg"

WELCOME_COLLECTION = get_collection("welcome")
LEFT_COLLECTION = get_collection("left")
WELCOME_CHATS = Filters.chat([])
LEFT_CHATS = Filters.chat([])


async def _init() -> None:
    async for i in WELCOME_COLLECTION.find({'on': True}, {'_id': 1}):
        WELCOME_CHATS.add(i.get('_id'))
    async for i in LEFT_COLLECTION.find({'on': True}, {'_id': 1}):
        LEFT_CHATS.add(i.get('_id'))


@userge.on_cmd("setwelcome", about={
    'header': "Creates a welcome message in current chat",
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{mention}': "mention user"},
    'types': [
        'audio', 'animation', 'document', 'photo',
        'sticker', 'voice', 'video_note', 'video'],
    'examples': [
        "{tr}setwelcome Hi {mention}, <b>Welcome</b> to {chat} chat\n"
        "or reply to supported media",
        "reply {tr}setwelcome to text message or supported media with text"],
    'others': "**max media size limt** : 10MB !"})
async def setwel(msg: Message):
    await raw_set(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("setleft", about={
    'header': "Creates a left message in current chat",
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{mention}': "mention user"},
    'types': [
        'audio', 'animation', 'document', 'photo',
        'sticker', 'voice', 'video_note', 'video'],
    'examples': [
        "{tr}setleft {flname}, Why you left :(\n"
        "or reply to supported media",
        "reply {tr}setleft to text message or supported media with text"],
    'others': "**max media size limt** : 10MB !"})
async def setleft(msg: Message):
    await raw_set(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("nowelcome", about={
    'header': "Disables and removes welcome message in the current chat"})
async def nowel(msg: Message):
    await raw_no(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("noleft", about={
    'header': "Disables and removes left message in the current chat"})
async def noleft(msg: Message):
    await raw_no(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("dowelcome", about={
    'header': "Turns on welcome message in the current chat"})
async def dowel(msg: Message):
    await raw_do(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("doleft", about={
    'header': "Turns on left message in the current chat :)"})
async def doleft(msg: Message):
    await raw_do(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("delwelcome", about={
    'header': "Delete welcome message in the current chat :)"})
async def delwel(msg: Message):
    await raw_del(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("delleft", about={
    'header': "Delete left message in the current chat :)"})
async def delleft(msg: Message):
    await raw_del(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("lswelcome", about={
    'header': "Shows the activated chats for welcome"})
async def lswel(msg: Message):
    await raw_ls(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("lsleft", about={
    'header': "Shows the activated chats for left"})
async def lsleft(msg: Message):
    await raw_ls(msg, 'Left', LEFT_COLLECTION)


@userge.on_cmd("vwelcome", about={
    'header': "Shows welcome message in current chat"})
async def viewwel(msg: Message):
    await raw_view(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("vleft", about={
    'header': "Shows left message in current chat"})
async def viewleft(msg: Message):
    await raw_view(msg, 'Left', LEFT_COLLECTION)


@userge.on_new_member(WELCOME_CHATS)
async def saywel(msg: Message):
    await raw_say(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_left_member(LEFT_CHATS)
async def sayleft(msg: Message):
    await raw_say(msg, 'Left', LEFT_COLLECTION)


async def raw_set(message: Message, name, collection, chats):
    if message.chat.type in ["private", "bot", "channel"]:
        await message.err(text=f'Are you high XO\nSet {name} in a group chat')
        return
    replied = message.reply_to_message
    string = message.input_or_reply_str
    file_ = ''
    file_type = ''
    if replied and replied.media:
        if replied.audio:
            file_ = replied.audio
            file_type = 'audio'
        elif replied.animation:
            file_ = replied.animation
            file_type = 'animation'
        elif replied.document:
            file_ = replied.document
            file_type = 'document'
        elif replied.photo:
            file_ = replied.photo
            file_type = 'photo'
        elif replied.sticker:
            file_ = replied.sticker
            file_type = 'sticker'
        elif replied.voice:
            file_ = replied.voice
            file_type = 'voice'
        elif replied.video_note:
            file_ = replied.video_note
            file_type = 'video_note'
        elif replied.video:
            file_ = replied.video
            file_type = 'video'
        if file_ and file_.file_size > 1024 * 1024 * 10:
            await message.err('File Size Too Large...!')
            return
    if not string and not file_:
        out = f"**Wrong Syntax**\nchech `.help .set{name.lower()}`"
    else:
        media = ''
        file_name = ''
        file_id = ''
        file_ref = ''
        if file_:
            file_id = file_.file_id
            file_ref = file_.file_ref
            c_time = time.time()
            tmp_path = await userge.download_media(
                message=file_,
                file_name=Config.DOWN_PATH,
                progress=progress,
                progress_args=(
                    "trying to download", userge, message, c_time
                )
            )
            async with aiofiles.open(tmp_path, "rb") as media_file:
                media = base64.b64encode(await media_file.read())
            file_name = os.path.basename(tmp_path)
            os.remove(tmp_path)

        await collection.update_one({'_id': message.chat.id},
                                    {"$set": {'data': string,
                                              'media': media,
                                              'type': file_type,
                                              'name': file_name,
                                              'fid': file_id,
                                              'fref': file_ref,
                                              'on': True}},
                                    upsert=True)
        chats.add(message.chat.id)
        out = f"{name} __message has been set for the__\n`{message.chat.title}`"
    await message.edit(text=out, del_in=3)


async def raw_no(message: Message, name, collection, chats):
    out = f"`First Set {name} Message!`"
    if await collection.find_one_and_update(
            {'_id': message.chat.id}, {"$set": {'on': False}}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)
        out = f"`{name} Disabled Successfully!`"
    await message.edit(text=out, del_in=3)


async def raw_do(message: Message, name, collection, chats):
    out = f'Please set the {name} message with `.set{name.lower()}`'
    if await collection.find_one_and_update(
            {'_id': message.chat.id}, {"$set": {'on': True}}):
        chats.add(message.chat.id)
        out = f'`I will {name} new members XD`'
    await message.edit(text=out, del_in=3)


async def raw_del(message: Message, name, collection, chats):
    out = f"`First Set {name} Message!`"
    if await collection.find_one_and_delete({'_id': message.chat.id}):
        if message.chat.id in chats:
            chats.remove(message.chat.id)
        out = f"`{name} Removed Successfully!`"
    await message.edit(text=out, del_in=3)


async def raw_view(message: Message, name, collection):
    liststr = ""
    found = await collection.find_one(
        {'_id': message.chat.id}, {'data': 1, 'type': 1, 'on': 1})
    if found:
        liststr += f"**{(await userge.get_chat(message.chat.id)).title}**\n"
        if 'type' in found and found['type']:
            liststr += f"`{found['type']}`\n"
        if 'data' in found and found['data']:
            liststr += f"`{found['data']}`\n"
        liststr += f"**Active:** `{found['on']}`"
    await message.edit(
        text=liststr or f'`NO {name.upper()} STARTED`', del_in=0)


async def raw_ls(message: Message, name, collection):
    liststr = ""
    async for c_l in collection.find({}, {'media': 0}):
        liststr += f"**{(await userge.get_chat(c_l['_id'])).title}**\n"
        if 'type' in c_l and c_l['type']:
            liststr += f"`{c_l['type']}`\n"
        if 'data' in c_l and c_l['data']:
            liststr += f"`{c_l['data']}`\n"
        liststr += f"**Active:** `{c_l['on']}`\n\n"
    await message.edit(
        text=liststr or f'`NO {name.upper()}S STARTED`', del_in=0)


async def raw_say(message: Message, name, collection):
    user = message.new_chat_members[0] if name == "Welcome" \
        else message.left_chat_member
    user_dict = await userge.get_user_dict(user.id)
    user_dict.update({'chat': message.chat.title if message.chat.title else "this group"})
    found = await collection.find_one({'_id': message.chat.id}, {'media': 0, 'name': 0})
    caption = found['data']
    file_type = found['type'] if 'type' in found else ''
    file_id = found['fid'] if 'fid' in found else ''
    file_ref = found['fref'] if 'fref' in found else ''
    if caption:
        caption = caption.format_map(SafeDict(**user_dict))
    if file_id:
        try:
            await send_proper_type(message, caption, file_type, file_id, file_ref)
        except (FileIdInvalid, FileReferenceEmpty, BadRequest):
            found = await collection.find_one({'_id': message.chat.id}, {'media': 1, 'name': 1})
            file_name = found['name']
            media = found['media']
            tmp_media_path = os.path.join(Config.DOWN_PATH, file_name)
            async with aiofiles.open(tmp_media_path, "wb") as media_file:
                await media_file.write(base64.b64decode(media))
            file_id, file_ref = await send_proper_type(message, caption, file_type, tmp_media_path)
            await collection.update_one({'_id': message.chat.id},
                                        {"$set": {'fid': file_id, 'fref': file_ref}},
                                        upsert=True)
            os.remove(tmp_media_path)
    else:
        await message.reply(caption, del_in=Config.WELCOME_DELETE_TIMEOUT)
    message.stop_propagation()


async def send_proper_type(message: Message,
                           caption: str,
                           file_type: str,
                           media: str,
                           file_ref: str = None) -> tuple:
    """sent proper type"""
    thumb = None
    if os.path.exists(THUMB_PATH):
        thumb = THUMB_PATH
    tmp_msgs = []
    if file_type == 'audio':
        duration = 0
        if os.path.exists(media):
            duration = extractMetadata(createParser(media)).get("duration").seconds
        msg = await userge.send_audio(chat_id=message.chat.id,
                                      audio=media,
                                      file_ref=file_ref,
                                      caption=caption,
                                      duration=duration,
                                      thumb=thumb,
                                      reply_to_message_id=message.message_id)

        file_id = msg.audio.file_id
        file_ref = msg.audio.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'animation':
        duration = 0
        if os.path.exists(media):
            duration = extractMetadata(createParser(media)).get("duration").seconds
            if not thumb:
                thumb = take_screen_shot(media, duration)
        msg = await userge.send_animation(chat_id=message.chat.id,
                                          animation=media,
                                          file_ref=file_ref,
                                          caption=caption,
                                          duration=duration,
                                          thumb=thumb,
                                          reply_to_message_id=message.message_id)
        file_id = msg.animation.file_id
        file_ref = msg.animation.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'photo':
        msg = await userge.send_photo(chat_id=message.chat.id,
                                      photo=media,
                                      file_ref=file_ref,
                                      caption=caption,
                                      reply_to_message_id=message.message_id)
        file_id = msg.photo.file_id
        file_ref = msg.photo.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'sticker':
        msg = await userge.send_sticker(chat_id=message.chat.id,
                                        sticker=media,
                                        file_ref=file_ref,
                                        reply_to_message_id=message.message_id)
        if caption:
            tmp_msgs.append(await message.reply(caption))
        file_id = msg.sticker.file_id
        file_ref = msg.sticker.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'voice':
        duration = 0
        if os.path.exists(media):
            duration = extractMetadata(createParser(media)).get("duration").seconds
        msg = await userge.send_voice(chat_id=message.chat.id,
                                      voice=media,
                                      file_ref=file_ref,
                                      caption=caption,
                                      duration=duration,
                                      reply_to_message_id=message.message_id)
        file_id = msg.voice.file_id
        file_ref = msg.voice.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'video_note':
        duration = 0
        if os.path.exists(media):
            duration = extractMetadata(createParser(media)).get("duration").seconds
            if not thumb:
                thumb = take_screen_shot(media, duration)
        msg = await userge.send_video_note(chat_id=message.chat.id,
                                           video_note=media,
                                           file_ref=file_ref,
                                           duration=duration,
                                           thumb=thumb,
                                           reply_to_message_id=message.message_id)
        if caption:
            tmp_msgs.append(await message.reply(caption))
        file_id = msg.video_note.file_id
        file_ref = msg.video_note.file_ref
        tmp_msgs.append(msg)

    elif file_type == 'video':
        duration = 0
        if os.path.exists(media):
            duration = extractMetadata(createParser(media)).get("duration").seconds
            if not thumb:
                thumb = take_screen_shot(media, duration)
        msg = await userge.send_video(chat_id=message.chat.id,
                                      video=media,
                                      file_ref=file_ref,
                                      caption=caption,
                                      duration=duration,
                                      thumb=thumb,
                                      reply_to_message_id=message.message_id)
        file_id = msg.video.file_id
        file_ref = msg.video.file_ref
        tmp_msgs.append(msg)

    else:
        msg = await userge.send_document(chat_id=message.chat.id,
                                         document=media,
                                         file_ref=file_ref,
                                         thumb=thumb,
                                         caption=caption,
                                         reply_to_message_id=message.message_id)
        file_id = msg.document.file_id
        file_ref = msg.document.file_ref
        tmp_msgs.append(msg)

    if Config.WELCOME_DELETE_TIMEOUT:
        await asyncio.sleep(Config.WELCOME_DELETE_TIMEOUT)
        for msg_ in tmp_msgs:
            if isinstance(msg_, RawMessage):
                await msg_.delete()
    return file_id, file_ref
