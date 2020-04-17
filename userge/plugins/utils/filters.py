# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, Filters, get_collection

FILTERS_COLLECTION = get_collection("filters")

FILTERS_CHATS = Filters.chat([])
FILTERS_DATA = {}


def _filter_updater(chat_id: int, name: str, content: str) -> None:
    dict_ = {}
    dict_[name] = content

    if chat_id in FILTERS_DATA:
        FILTERS_DATA[chat_id].update(dict_)

    else:
        FILTERS_DATA[chat_id] = dict_
        FILTERS_CHATS.add(chat_id)


def _filter_deleter(chat_id: int, name: str) -> None:
    if chat_id in FILTERS_DATA and name in FILTERS_DATA[chat_id]:
        FILTERS_DATA[chat_id].pop(name)

        if not FILTERS_DATA[chat_id]:
            FILTERS_DATA.pop(chat_id)
            FILTERS_CHATS.remove(chat_id)


for flt in FILTERS_COLLECTION.find():
    _filter_updater(flt['chat_id'], flt['name'], flt['content'])


@userge.on_cmd("filters", about="__List all saved filters__")
async def filters_active(message: Message):
    out = ''
    for filter_ in FILTERS_DATA[message.chat.id]:
        out += " 🔍 `{}`\n".format(filter_)

    if out:
        await message.edit("**--Filters saved in this chat:--**\n\n" + out, del_in=0)

    else:
        await message.err("There are no saved filters in this chat")


@userge.on_cmd("delfilter", about="""\
__Deletes a filter by name__

**Usage:**

    `.delfilter [filter name]`""")
async def delete_filters(message: Message):
    filter_ = message.input_str

    if not filter_:
        out = "`Wrong syntax`\nNo arguements"

    elif FILTERS_COLLECTION.find_one_and_delete({'chat_id': message.chat.id, 'name': filter_}):
        out = "`Successfully deleted filter:` **{}**".format(filter_)
        _filter_deleter(message.chat.id, filter_)

    else:
        out = "`Couldn't find filter:` **{}**".format(filter_)

    await message.edit(text=out, del_in=3)


@userge.on_cmd(r"addfilter (\w[^\|]*)(?:\s?\|\s?([\s\S]+))?",
               about="""\
__Adds a filter by name__

**Usage:**

    `.addfilter [filter name] | [content | reply to msg]`""")
async def add_filter(message: Message):
    filter_ = message.matches[0].group(1).strip()
    content = message.matches[0].group(2)

    if message.reply_to_message:
        content = message.reply_to_message.text

    print(filter_, content)

    if not content:
        await message.err(text="No Content Found!")
        return

    _filter_updater(message.chat.id, filter_, content.strip())

    out = "`{} filter -> {}`"
    result = FILTERS_COLLECTION.update_one({'chat_id': message.chat.id, 'name': filter_},
                                           {"$set": {'content': content.strip()}},
                                           upsert=True)

    if result.upserted_id:
        out = out.format('Added', filter_)

    else:
        out = out.format('Updated', filter_)

    await message.edit(text=out, del_in=3, log=True)


@userge.on_filters(FILTERS_CHATS)
async def chat_filter(message: Message):
    for name in FILTERS_DATA[message.chat.id]:
        if name in message.text:
            await message.reply(FILTERS_DATA[message.chat.id][name])
    message.continue_propagation()
