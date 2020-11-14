""" setup notes """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Dict, Tuple

from userge import userge, Message, get_collection, Config

NOTES_COLLECTION = get_collection("notes")
CHANNEL = userge.getCLogger(__name__)

NOTES_DATA: Dict[int, Dict[str, Tuple[int, bool]]] = {}


def _note_updater(chat_id: int, name: str, message_id: int, is_global: bool) -> None:
    if chat_id in NOTES_DATA:
        NOTES_DATA[chat_id].update({name: (message_id, is_global)})
    else:
        NOTES_DATA[chat_id] = {name: (message_id, is_global)}


def _note_deleter(chat_id: int, name: str) -> None:
    if chat_id in NOTES_DATA and name in NOTES_DATA[chat_id]:
        NOTES_DATA[chat_id].pop(name)
        if not NOTES_DATA[chat_id]:
            NOTES_DATA.pop(chat_id)


def _get_notes_for_chat(chat_id: int) -> str:
    out = ''
    if chat_id in NOTES_DATA:
        for name, pack in NOTES_DATA[chat_id].items():
            mid, is_global = pack
            out += " 📌 `{}` [**{}**] , {}\n".format(
                name, 'G' if is_global else 'L', CHANNEL.get_link(mid))
    return out


async def _init() -> None:
    async for nt in NOTES_COLLECTION.find():
        if 'mid' not in nt:
            continue
        _note_updater(nt['chat_id'], nt['name'], nt['mid'], nt['global'])


@userge.on_cmd(
    "notes", about={
        'header': "List all saved notes in current chat",
        'flags': {'-all': "List all saved notes in every chats"}},
    allow_channels=False, allow_bots=False)
async def view_notes(message: Message) -> None:
    """ list notes in current chat """
    out = ''
    if '-all' in message.flags:
        await message.edit("`getting notes ...`")
        for chat_id in NOTES_DATA:
            out += f"**{(await message.client.get_chat(chat_id)).title}**\n"
            out += _get_notes_for_chat(chat_id)
            out += '\n'
        if out:
            out = "**--Notes saved in every chats:--**\n\n" + out
    else:
        out = _get_notes_for_chat(message.chat.id)
        if out:
            out = "**--Notes saved in this chat:--**\n\n" + out
    if out:
        await message.edit(out, del_in=0)
    else:
        await message.err("There are no saved notes in this chat")


@userge.on_cmd(
    "delnote", about={
        'header': "Deletes a note by name",
        'flags': {
            '-all': "remove all notes in this chat",
            '-every': "remove all notes in every chats"},
        'usage': "{tr}delnote [note name]\n{tr}delnote -all"},
    allow_channels=False, allow_bots=False)
async def remove_note(message: Message) -> None:
    """ delete note in current chat """
    if '-every' in message.flags:
        NOTES_DATA.clear()
        await asyncio.gather(
            NOTES_COLLECTION.drop(),
            message.edit("`Cleared All Notes in Every Chat !`", del_in=5))
        return
    if '-all' in message.flags:
        if message.chat.id in NOTES_DATA:
            del NOTES_DATA[message.chat.id]
            await asyncio.gather(
                NOTES_COLLECTION.delete_many({'chat_id': message.chat.id}),
                message.edit("`Cleared All Notes in This Chat !`", del_in=5))
        else:
            await message.err("Couldn't find notes in this chat!")
        return
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_delete(
            {'chat_id': message.chat.id, 'name': notename}):
        out = "`Successfully deleted note:` **{}**".format(notename)
        _note_deleter(message.chat.id, notename)
    else:
        out = "`Couldn't find note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(
    "gtlnote", about={
        'header': "global note to local note",
        'description': "only sudos and owner can access local notes",
        'usage': "{tr}gtlnote [note name]"},
    allow_channels=False, allow_bots=False)
async def mv_to_local_note(message: Message) -> None:
    """ global to local note """
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_update(
            {'chat_id': message.chat.id, 'name': notename, 'global': True},
            {"$set": {'global': False}}):
        out = "`Successfully transferred to local note:` **{}**".format(notename)
        NOTES_DATA[message.chat.id][notename] = (NOTES_DATA[message.chat.id][notename][0], False)
    else:
        out = "`Couldn't find global note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(
    "ltgnote", about={
        'header': "local note to global note",
        'description': "anyone can access global notes",
        'usage': "{tr}ltgnote [note name]"},
    allow_channels=False, allow_bots=False)
async def mv_to_global_note(message: Message) -> None:
    """ local to global note """
    notename = message.input_str
    if not notename:
        out = "`Wrong syntax`\nNo arguements"
    elif await NOTES_COLLECTION.find_one_and_update(
            {'chat_id': message.chat.id, 'name': notename, 'global': False},
            {"$set": {'global': True}}):
        out = "`Successfully transferred to global note:` **{}**".format(notename)
        NOTES_DATA[message.chat.id][notename] = (NOTES_DATA[message.chat.id][notename][0], True)
    else:
        out = "`Couldn't find local note:` **{}**".format(notename)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(r"(?:#|get\s)(\S+)",
               about={'header': "Gets a note by name",
                      'usage': "#[notename]\nget notename"},
               group=-1,
               name="get_note",
               trigger='',
               filter_me=False,
               check_client=True)
async def get_note(message: Message) -> None:
    """ get any saved note """
    if not message.from_user:
        return
    if message.chat.id not in NOTES_DATA:
        return
    can_access = message.from_user.is_self or message.from_user.id in Config.SUDO_USERS
    if Config.OWNER_ID:
        can_access = can_access or message.from_user.id in Config.OWNER_ID
    notename = message.matches[0].group(1).lower()
    mid, is_global = (0, False)
    for note in NOTES_DATA[message.chat.id]:
        if note.lower() == notename:
            mid, is_global = NOTES_DATA[message.chat.id][note]
            break
    if not mid:
        return
    if can_access or is_global:
        replied = message.reply_to_message
        user_id = message.from_user.id
        if replied:
            reply_to_message_id = replied.message_id
            if replied.from_user:
                user_id = replied.from_user.id
        else:
            reply_to_message_id = message.message_id
        await CHANNEL.forward_stored(client=message.client,
                                     message_id=mid,
                                     chat_id=message.chat.id,
                                     user_id=user_id,
                                     reply_to_message_id=reply_to_message_id)


@userge.on_cmd(
    r"addnote (\S+)(?:\s([\s\S]+))?", about={
        'header': "Adds a note by name",
        'options': {
            '{fname}': "add first name",
            '{lname}': "add last name",
            '{flname}': "add full name",
            '{uname}': "username",
            '{chat}': "chat name",
            '{count}': "chat members count",
            '{mention}': "mention user"},
        'usage': "{tr}addnote [note name] [content | reply to msg]",
        'buttons': "<code>[name][buttonurl:link]</code> - <b>add a url button</b>\n"
                   "<code>[name][buttonurl:link:same]</code> - "
                   "<b>add a url button to same row</b>"},
    allow_channels=False, allow_bots=False)
async def add_note(message: Message) -> None:
    """ add note to curent chat """
    notename = message.matches[0].group(1)
    content = message.matches[0].group(2)
    replied = message.reply_to_message
    if replied and replied.text:
        content = replied.text.html
    content = "📝 **Note** : `{}`\n\n{}".format(notename, content or '')
    if not (content or (replied and replied.media)):
        await message.err(text="No Content Found!")
        return
    await message.edit("`adding note ...`")
    message_id = await CHANNEL.store(replied, content)
    result = await NOTES_COLLECTION.update_one(
        {'chat_id': message.chat.id, 'name': notename},
        {"$set": {'mid': message_id, 'global': False}}, upsert=True)
    _note_updater(message.chat.id, notename, message_id, False)
    out = "`{} note #{}`"
    if result.upserted_id:
        out = out.format('Added', notename)
    else:
        out = out.format('Updated', notename)
    await message.edit(text=out, del_in=3, log=__name__)
