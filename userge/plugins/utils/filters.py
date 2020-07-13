""" setup filters """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from typing import Dict

from userge import userge, Message, Filters, get_collection

FILTERS_COLLECTION = get_collection("filters")

FILTERS_DATA: Dict[int, Dict[str, int]] = {}
FILTERS_CHATS = Filters.create(lambda _, query: query.chat.id in FILTERS_DATA)
CHANNEL = userge.getCLogger(__name__)


def _filter_updater(chat_id: int, name: str, message_id: int) -> None:
    if chat_id in FILTERS_DATA:
        FILTERS_DATA[chat_id].update({name: message_id})
    else:
        FILTERS_DATA[chat_id] = {name: message_id}


def _filter_deleter(chat_id: int, name: str) -> None:
    if chat_id in FILTERS_DATA and name in FILTERS_DATA[chat_id]:
        FILTERS_DATA[chat_id].pop(name)
        if not FILTERS_DATA[chat_id]:
            FILTERS_DATA.pop(chat_id)


async def _init() -> None:
    async for flt in FILTERS_COLLECTION.find():
        if 'mid' not in flt:
            continue
        _filter_updater(flt['chat_id'], flt['name'], flt['mid'])


@userge.on_cmd(
    "filters", about={
        'header': "List all saved filters in current chat"},
    allow_channels=False, allow_bots=False, allow_via_bot=False)
async def filters_active(message: Message) -> None:
    """ list filters in current chat """
    out = ''
    if message.chat.id in FILTERS_DATA:
        for name, mid in FILTERS_DATA[message.chat.id].items():
            if not isinstance(mid, int):
                continue
            out += " 🔍 `{}` , {}\n".format(name, CHANNEL.get_link(mid))
    if out:
        await message.edit("**--Filters saved in this chat:--**\n\n" + out, del_in=0)
    else:
        await message.err("There are no saved filters in this chat")


@userge.on_cmd(
    "delfilter", about={
        'header': "Deletes a filter by name",
        'usage': "{tr}delfilter [filter name]"},
    allow_channels=False, allow_bots=False, allow_via_bot=False)
async def delete_filters(message: Message) -> None:
    """ delete filter in current chat """
    filter_ = message.input_str
    if not filter_:
        out = "`Wrong syntax`\nNo arguements"
    elif await FILTERS_COLLECTION.find_one_and_delete(
            {'chat_id': message.chat.id, 'name': filter_}):
        out = "`Successfully deleted filter:` **{}**".format(filter_)
        _filter_deleter(message.chat.id, filter_)
    else:
        out = "`Couldn't find filter:` **{}**".format(filter_)
    await message.edit(text=out, del_in=3)


@userge.on_cmd(r"addfilter ([^\s\|][^\|]*)(?:\s?\|\s?([\s\S]+))?",
               about={
                   'header': "Adds a filter by name",
                   'options': {
                       '{fname}': "add first name",
                       '{lname}': "add last name",
                       '{flname}': "add full name",
                       '{uname}': "username",
                       '{chat}': "chat name",
                       '{count}': "chat members count",
                       '{mention}': "mention user"},
                   'usage': "{tr}addfilter [filter name] | [content | reply to msg]"},
               allow_channels=False, allow_bots=False, allow_via_bot=False)
async def add_filter(message: Message) -> None:
    """ add filter to current chat """
    filter_ = message.matches[0].group(1).strip()
    content = message.matches[0].group(2)
    replied = message.reply_to_message
    if replied and replied.text:
        content = replied.text.html
    if not (content or (replied and replied.media)):
        await message.err(text="No Content Found!")
        return
    message_id = await CHANNEL.store(replied, content)
    _filter_updater(message.chat.id, filter_, message_id)
    result = await FILTERS_COLLECTION.update_one(
        {'chat_id': message.chat.id, 'name': filter_},
        {"$set": {'mid': message_id}}, upsert=True)
    out = "`{} filter -> {}`"
    if result.upserted_id:
        out = out.format('Added', filter_)
    else:
        out = out.format('Updated', filter_)
    await message.edit(text=out, del_in=3, log=True)


@userge.on_filters(~Filters.me & Filters.text & FILTERS_CHATS, group=1, allow_via_bot=False)
async def chat_filter(message: Message) -> None:
    """ filter handler """
    if not message.from_user:
        return
    input_text = message.text.strip()
    for name in FILTERS_DATA[message.chat.id]:
        if (input_text == name
                or input_text.startswith(f"{name} ")
                or input_text.endswith(f" {name}")
                or f" {name} " in input_text):
            await CHANNEL.forward_stored(message_id=FILTERS_DATA[message.chat.id][name],
                                         chat_id=message.chat.id,
                                         user_id=message.from_user.id,
                                         reply_to_message_id=message.message_id)
