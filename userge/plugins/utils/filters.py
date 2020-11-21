""" setup filters """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
from typing import Dict

from userge import userge, Message, filters, get_collection

FILTERS_COLLECTION = get_collection("filters")
CHANNEL = userge.getCLogger(__name__)

FILTERS_DATA: Dict[int, Dict[str, int]] = {}
FILTERS_CHATS = filters.create(lambda _, __, query: query.chat and query.chat.id in FILTERS_DATA)

_SUPPORTED_TYPES = (":audio:", ":video:", ":photo:", ":document:",
                    ":sticker:", ":animation:", ":voice:", ":video_note:",
                    ":media:", ":game:", ":contact:", ":location:",
                    ":venue:", ":web_page:", ":poll:", ":via_bot:",
                    ":forward_date:", ":mentioned:", ":service:",
                    ":media_group_id:", ":game_high_score:", ":pinned_message:",
                    ":new_chat_title:", ":new_chat_photo:", ":delete_chat_photo:")


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


def _get_filters_for_chat(chat_id: int) -> str:
    out = ''
    if chat_id in FILTERS_DATA:
        for name, mid in FILTERS_DATA[chat_id].items():
            if not isinstance(mid, int):
                continue
            out += " 🔍 `{}` , {}\n".format(name, CHANNEL.get_link(mid))
    return out


async def _init() -> None:
    async for flt in FILTERS_COLLECTION.find():
        if 'mid' not in flt:
            continue
        _filter_updater(flt['chat_id'], flt['name'], flt['mid'])


@userge.on_cmd(
    "filters", about={
        'header': "List all saved filters in current chat",
        'flags': {'-all': "List all saved filters in every chats"}},
    allow_channels=False, allow_bots=False)
async def filters_active(message: Message) -> None:
    """ list filters in current chat """
    out = ''
    if '-all' in message.flags:
        await message.edit("`getting filters ...`")
        for chat_id in FILTERS_DATA:
            out += f"**{(await message.client.get_chat(chat_id)).title}**\n"
            out += _get_filters_for_chat(chat_id)
            out += '\n'
        if out:
            out = "**--Filters saved in every chats:--**\n\n" + out
    else:
        out = _get_filters_for_chat(message.chat.id)
        if out:
            out = "**--Filters saved in this chat:--**\n\n" + out
    if out:
        await message.edit(out, del_in=0)
    else:
        await message.err("There are no saved filters in this chat")


@userge.on_cmd(
    "delfilter", about={
        'header': "Deletes a filter by name",
        'flags': {
            '-all': "remove all filters in this chat",
            '-every': "remove all filters in every chats"},
        'usage': "{tr}delfilter [filter name | filter type]\n{tr}delfilter -all"},
    allow_channels=False, allow_bots=False)
async def delete_filters(message: Message) -> None:
    """ delete filter in current chat """
    if '-every' in message.flags:
        FILTERS_DATA.clear()
        await asyncio.gather(
            FILTERS_COLLECTION.drop(),
            message.edit("`Cleared All Filters in Every Chat !`", del_in=5))
        return
    if '-all' in message.flags:
        if message.chat.id in FILTERS_DATA:
            del FILTERS_DATA[message.chat.id]
            await asyncio.gather(
                FILTERS_COLLECTION.delete_many({'chat_id': message.chat.id}),
                message.edit("`Cleared All Filters in This Chat !`", del_in=5))
        else:
            await message.err("Couldn't find filters in this chat!")
        return
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


@userge.on_cmd(
    r"addfilter ([^\s\|][^\|]*)(?:\s?\|\s?([\s\S]+))?", about={
        'header': "Adds a filter by name",
        'options': {
            '{fname}': "add first name",
            '{lname}': "add last name",
            '{flname}': "add full name",
            '{uname}': "username",
            '{chat}': "chat name",
            '{count}': "chat members count",
            '{mention}': "mention user"},
        'usage': "{tr}addfilter [filter name | filter type] | [content | reply to msg]",
        'types': list(_SUPPORTED_TYPES),
        'buttons': "<code>[name][buttonurl:link]</code> - <b>add a url button</b>\n"
                   "<code>[name][buttonurl:link:same]</code> - "
                   "<b>add a url button to same row</b>"},
    allow_channels=False, allow_bots=False)
async def add_filter(message: Message) -> None:
    """ add filter to current chat """
    filter_ = message.matches[0].group(1).strip()
    content = message.matches[0].group(2)
    replied = message.reply_to_message
    if replied and replied.text:
        content = replied.text.html
    if not (content or (replied and replied.media)):
        await message.err("No Content Found !")
        return
    if (filter_.startswith(':') and filter_.endswith(':')
            and filter_ not in _SUPPORTED_TYPES):
        await message.err(f"invalid media type [ {filter_} ] !")
        return
    await message.edit("`adding filter ...`")
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
    await message.edit(text=out, del_in=3, log=__name__)


@userge.on_filters(~filters.me & ~filters.edited & FILTERS_CHATS, group=1)
async def chat_filter(message: Message) -> None:
    """ filter handler """
    if not message.from_user:
        return
    try:
        for name in FILTERS_DATA[message.chat.id]:
            reply = False
            if name.startswith(':') and name.endswith(':'):
                media_type = name.strip(':')
                if getattr(message, media_type, None):
                    reply = True
            elif message.text:
                l_name = name.lower()
                input_text = message.text.strip().lower()
                if (input_text == l_name
                        or input_text.startswith(f"{l_name} ")
                        or input_text.endswith(f" {l_name}")
                        or f" {l_name} " in input_text):
                    reply = True
            if reply:
                await CHANNEL.forward_stored(client=message.client,
                                             message_id=FILTERS_DATA[message.chat.id][name],
                                             chat_id=message.chat.id,
                                             user_id=message.from_user.id,
                                             reply_to_message_id=message.message_id)
    except RuntimeError:
        pass
