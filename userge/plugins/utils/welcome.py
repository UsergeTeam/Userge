""" auto welcome and left messages """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Filters, Message, Config, get_collection

WELCOME_COLLECTION = get_collection("welcome")
LEFT_COLLECTION = get_collection("left")
WELCOME_CHATS = Filters.chat([])
LEFT_CHATS = Filters.chat([])
CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    async for i in WELCOME_COLLECTION.find({'on': True}):
        if 'mid' not in i:
            continue
        WELCOME_CHATS.add(i.get('_id'))
    async for i in LEFT_COLLECTION.find({'on': True}):
        if 'mid' not in i:
            continue
        LEFT_CHATS.add(i.get('_id'))


@userge.on_cmd("setwelcome", about={
    'header': "Creates a welcome message in current chat",
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{count}': "chat members count",
        '{mention}': "mention user"},
    'types': [
        'audio', 'animation', 'document', 'photo',
        'sticker', 'voice', 'video_note', 'video'],
    'examples': [
        "{tr}setwelcome Hi {mention}, <b>Welcome</b> to {chat} chat\n"
        "or reply to supported media",
        "reply {tr}setwelcome to text message or supported media with text"],
    'buttons': "<code>[name][buttonurl:link]</code> - <b>add a url button</b>\n"
               "<code>[name][buttonurl:link:same]</code> - <b>add a url button to same row</b>"},
    allow_channels=False, allow_bots=False, allow_private=False)
async def setwel(msg: Message):
    """ set welcome message """
    await raw_set(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("setleft", about={
    'header': "Creates a left message in current chat",
    'options': {
        '{fname}': "add first name",
        '{lname}': "add last name",
        '{flname}': "add full name",
        '{uname}': "username",
        '{chat}': "chat name",
        '{count}': "chat members count",
        '{mention}': "mention user"},
    'types': [
        'audio', 'animation', 'document', 'photo',
        'sticker', 'voice', 'video_note', 'video'],
    'examples': [
        "{tr}setleft {flname}, Why you left :(\n"
        "or reply to supported media",
        "reply {tr}setleft to text message or supported media with text"],
    'buttons': "<code>[name][buttonurl:link]</code> - <b>add a url button</b>\n"
               "<code>[name][buttonurl:link:same]</code> - <b>add a url button to same row</b>"},
    allow_channels=False, allow_bots=False, allow_private=False)
async def setleft(msg: Message):
    """ set left message """
    await raw_set(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("nowelcome", about={
    'header': "Disables welcome message in the current chat",
    'flags': {'-all': "disable all welcome messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def nowel(msg: Message):
    """ disable welcome message """
    await raw_no(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("noleft", about={
    'header': "Disables left message in the current chat",
    'flags': {'-all': "disable all left messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def noleft(msg: Message):
    """ disable left message """
    await raw_no(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("dowelcome", about={
    'header': "Turns on welcome message in the current chat",
    'flags': {'-all': "enable all welcome messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def dowel(msg: Message):
    """ enable welcome message """
    await raw_do(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("doleft", about={
    'header': "Turns on left message in the current chat :)",
    'flags': {'-all': "enable all left messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def doleft(msg: Message):
    """ enable left message """
    await raw_do(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("delwelcome", about={
    'header': "Delete welcome message in the current chat :)",
    'flags': {'-all': "delete all welcome messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def delwel(msg: Message):
    """ delete welcome message """
    await raw_del(msg, 'Welcome', WELCOME_COLLECTION, WELCOME_CHATS)


@userge.on_cmd("delleft", about={
    'header': "Delete left message in the current chat :)",
    'flags': {'-all': "delete all left messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def delleft(msg: Message):
    """ delete left messaage """
    await raw_del(msg, 'Left', LEFT_COLLECTION, LEFT_CHATS)


@userge.on_cmd("vwelcome", about={
    'header': "Shows welcome message in current chat",
    'flags': {'-all': "view all welcome messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def viewwel(msg: Message):
    """ view welcome message """
    await raw_view(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_cmd("vleft", about={
    'header': "Shows left message in current chat",
    'flags': {'-all': "view all left messages"}},
    allow_channels=False, allow_bots=False, allow_private=False)
async def viewleft(msg: Message):
    """ view left message """
    await raw_view(msg, 'Left', LEFT_COLLECTION)


@userge.on_new_member(WELCOME_CHATS)
async def saywel(msg: Message):
    """ welcome message handler """
    await raw_say(msg, 'Welcome', WELCOME_COLLECTION)


@userge.on_left_member(LEFT_CHATS)
async def sayleft(msg: Message):
    """ left message handler """
    await raw_say(msg, 'Left', LEFT_COLLECTION)


async def raw_set(message: Message, name, collection, chats):
    replied = message.reply_to_message
    string = message.input_or_reply_raw
    if not (string or (replied and replied.media)):
        out = f"**Wrong Syntax**\ncheck `.help .set{name.lower()}`"
    else:
        message_id = await CHANNEL.store(replied, string)
        await collection.update_one({'_id': message.chat.id},
                                    {"$set": {'mid': message_id, 'on': True}},
                                    upsert=True)
        chats.add(message.chat.id)
        out = f"{name} __message has been set for the__\n`{message.chat.title}`"
    await message.edit(text=out, del_in=3)


async def raw_no(message: Message, name, collection, chats):
    if '-all' in message.flags:
        async for c_l in collection.find({'on': True}):
            if 'mid' not in c_l:
                continue
            chats.remove(c_l['_id'])
        await collection.update_many({}, {"$set": {'on': False}})
        out = f"`All {name} Messages Disabled Successfully!`"
    else:
        out = f"`First Set {name} Message!`"
        if await collection.find_one_and_update(
                {'_id': message.chat.id}, {"$set": {'on': False}}):
            if message.chat.id in chats:
                chats.remove(message.chat.id)
            out = f"`{name} Disabled Successfully!`"
    await message.edit(text=out, del_in=3)


async def raw_do(message: Message, name, collection, chats):
    if '-all' in message.flags:
        async for c_l in collection.find({'on': False}):
            if 'mid' not in c_l:
                continue
            chats.add(c_l['_id'])
        await collection.update_many({}, {"$set": {'on': True}})
        out = f"`All {name} Messages Enabled Successfully!`"
    else:
        out = f'Please set the {name} message with `.set{name.lower()}`'
        if await collection.find_one_and_update(
                {'_id': message.chat.id}, {"$set": {'on': True}}):
            chats.add(message.chat.id)
            out = f'`I will {name} new members XD`'
    await message.edit(text=out, del_in=3)


async def raw_del(message: Message, name, collection, chats):
    out = f"`First Set {name} Message!`"
    if '-all' in message.flags:
        if chats:
            chats.clear()
            await collection.drop()
            out = f"`All {name} Messages Removed Successfully!`"
    else:
        if await collection.find_one_and_delete({'_id': message.chat.id}):
            if message.chat.id in chats:
                chats.remove(message.chat.id)
            out = f"`{name} Removed Successfully!`"
    await message.edit(text=out, del_in=3)


async def raw_view(message: Message, name, collection):
    liststr = ""
    if '-all' in message.flags:
        await message.edit(f"`getting {name.lower()}s ...`")
        async for c_l in collection.find():
            if 'mid' not in c_l:
                continue
            liststr += f"**{(await message.client.get_chat(c_l['_id'])).title}**\n"
            liststr += f"**Active:** `{c_l['on']}` , {CHANNEL.get_link(c_l['mid'])}\n\n"
    else:
        found = await collection.find_one({'_id': message.chat.id})
        if found:
            if 'mid' not in found:
                return
            liststr += f"**{(await message.client.get_chat(message.chat.id)).title}**\n"
            liststr += f"**Active:** `{found['on']}` , {CHANNEL.get_link(found['mid'])}"
    await message.edit(
        text=liststr or f'`NO {name.upper()} STARTED`', del_in=0)


async def raw_say(message: Message, name, collection):
    users = message.new_chat_members if name == "Welcome" else [message.left_chat_member]
    for user in users:
        found = await collection.find_one({'_id': message.chat.id})
        if 'mid' not in found:
            return
        await CHANNEL.forward_stored(client=message.client,
                                     message_id=found['mid'],
                                     chat_id=message.chat.id,
                                     user_id=user.id,
                                     reply_to_message_id=message.message_id,
                                     del_in=Config.WELCOME_DELETE_TIMEOUT)
    message.stop_propagation()


# async def send_proper_type(message: Message,
#                            caption: str,
#                            file_type: str,
#                            media: str,
#                            file_ref: str = None) -> tuple:
#     """sent proper type"""
#     thumb = None
#     if os.path.exists(THUMB_PATH):
#         thumb = THUMB_PATH
#     tmp_msgs = []
#     if file_type == 'audio':
#         duration = 0
#         if os.path.exists(media):
#             duration = extractMetadata(createParser(media)).get("duration").seconds
#         msg = await userge.send_audio(chat_id=message.chat.id,
#                                       audio=media,
#                                       file_ref=file_ref,
#                                       caption=caption,
#                                       duration=duration,
#                                       thumb=thumb,
#                                       reply_to_message_id=message.message_id)

#         file_id = msg.audio.file_id
#         file_ref = msg.audio.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'animation':
#         duration = 0
#         if os.path.exists(media):
#             duration = extractMetadata(createParser(media)).get("duration").seconds
#             if not thumb:
#                 thumb = take_screen_shot(media, duration)
#         msg = await userge.send_animation(chat_id=message.chat.id,
#                                           animation=media,
#                                           file_ref=file_ref,
#                                           caption=caption,
#                                           duration=duration,
#                                           thumb=thumb,
#                                           reply_to_message_id=message.message_id)
#         file_id = msg.animation.file_id
#         file_ref = msg.animation.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'photo':
#         msg = await userge.send_photo(chat_id=message.chat.id,
#                                       photo=media,
#                                       file_ref=file_ref,
#                                       caption=caption,
#                                       reply_to_message_id=message.message_id)
#         file_id = msg.photo.file_id
#         file_ref = msg.photo.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'sticker':
#         msg = await userge.send_sticker(chat_id=message.chat.id,
#                                         sticker=media,
#                                         file_ref=file_ref,
#                                         reply_to_message_id=message.message_id)
#         if caption:
#             tmp_msgs.append(await message.reply(caption))
#         file_id = msg.sticker.file_id
#         file_ref = msg.sticker.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'voice':
#         duration = 0
#         if os.path.exists(media):
#             duration = extractMetadata(createParser(media)).get("duration").seconds
#         msg = await userge.send_voice(chat_id=message.chat.id,
#                                       voice=media,
#                                       file_ref=file_ref,
#                                       caption=caption,
#                                       duration=duration,
#                                       reply_to_message_id=message.message_id)
#         file_id = msg.voice.file_id
#         file_ref = msg.voice.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'video_note':
#         duration = 0
#         if os.path.exists(media):
#             duration = extractMetadata(createParser(media)).get("duration").seconds
#             if not thumb:
#                 thumb = take_screen_shot(media, duration)
#         msg = await userge.send_video_note(chat_id=message.chat.id,
#                                            video_note=media,
#                                            file_ref=file_ref,
#                                            duration=duration,
#                                            thumb=thumb,
#                                            reply_to_message_id=message.message_id)
#         if caption:
#             tmp_msgs.append(await message.reply(caption))
#         file_id = msg.video_note.file_id
#         file_ref = msg.video_note.file_ref
#         tmp_msgs.append(msg)

#     elif file_type == 'video':
#         duration = 0
#         if os.path.exists(media):
#             duration = extractMetadata(createParser(media)).get("duration").seconds
#             if not thumb:
#                 thumb = take_screen_shot(media, duration)
#         msg = await userge.send_video(chat_id=message.chat.id,
#                                       video=media,
#                                       file_ref=file_ref,
#                                       caption=caption,
#                                       duration=duration,
#                                       thumb=thumb,
#                                       reply_to_message_id=message.message_id)
#         file_id = msg.video.file_id
#         file_ref = msg.video.file_ref
#         tmp_msgs.append(msg)

#     else:
#         msg = await userge.send_document(chat_id=message.chat.id,
#                                          document=media,
#                                          file_ref=file_ref,
#                                          thumb=thumb,
#                                          caption=caption,
#                                          reply_to_message_id=message.message_id)
#         file_id = msg.document.file_id
#         file_ref = msg.document.file_ref
#         tmp_msgs.append(msg)

#     if Config.WELCOME_DELETE_TIMEOUT:
#         await asyncio.sleep(Config.WELCOME_DELETE_TIMEOUT)
#         for msg_ in tmp_msgs:
#             if isinstance(msg_, RawMessage):
#                 await msg_.delete()
#     return file_id, file_ref
