"""SNIPS"""



# Based on notes.py

import asyncio

from userge import get_collection, userge, Message

CHANNEL = userge.getCLogger(__name__)

SNIPS = get_collection("SNIPS")

@userge.on_cmd("snips", about={

    'header': "List All Snips",

    'info': "Snips are Basicially like notes but across all groups and chats"})

async def _list_all_snips_(message: Message)-> None:

    """list all snips"""

    all_snips = "<b><u>All Saved SNIPS</u></b>\n\n"  

    async for data in SNIPS.find(): 

        all_snips += "• <code>${}</code>  {}\n".format(

            data['snip_name'], CHANNEL.get_link(data['snip_msg_id']))

    await message.edit(all_snips, del_in=20)

@userge.on_cmd(r"(?:\$|getsnip\s)(\S+)$",

        about={

            'header': "Get a snip by getsnip or \'$\' trigger",

            'usage': "$[snip]\ngetsnip [snip]"},

        name="get_snip",

        trigger='',

        filter_me=True,

        check_client=True)

async def get_snip(message: Message)-> None:

    """get a snip"""

    reply = message.reply_to_message

    reply_id = reply.message_id if reply else None

    snip_name = message.matches[0].group(1)

    found = await SNIPS.find_one({'snip_name': snip_name})

    if found:

        await message.delete()

        await CHANNEL.forward_stored(

            client=message.client, 

            message_id=found['snip_msg_id'],

            user_id=message.from_user.id,

            chat_id=message.chat.id,

            reply_to_message_id=reply_id

        )

@userge.on_cmd(r"addsnip (\S+)(?:\s([\s\S]+))?", about={

        'header': "Adds a snip by name",

        'usage': "{tr}addsnip [snip name] [content | reply to msg]"})

async def add_snip(message: Message) -> None:

    """add a snip"""

    snip_name = message.matches[0].group(1)

    content = message.matches[0].group(2)

    reply = message.reply_to_message

    if reply and reply.text:

        content = reply.text.html

    content = "{}".format(content or '')

    if not (content or (reply and reply.media)):

        await message.err("No Content Found!")

        return

    await message.edit("adding snip ...")

    message_id = await CHANNEL.store(reply, content)

    result = await SNIPS.update_one({'snip_name': snip_name}, {"$set": {'snip_msg_id': message_id}}, upsert=True)

    out = "{} Snip <b>${}</b>"

    if result.upserted_id:

        out = out.format('Added', snip_name)

    else:

        out = out.format('Updated', snip_name)

    await message.edit(text=out, del_in=5, log=__name__)

@userge.on_cmd("remsnip", about={

        'header': "Remove a snip by name",

        'flags': {

            '-all': "remove all saved snips"

        },

        'usage': "{tr}remsnip [snip name]\n{tr}remsnip -all"

        }, allow_channels=False, allow_bots=False)

async def rem_snip(message: Message)-> None:

    """remove a snip"""

    if '-all' in message.flags:

        await asyncio.gather(

            SNIPS.drop(),

            message.edit("`Cleared All SNIPS !`", del_in=5))

        return

    snip_name = message.input_str

    if not snip_name:

        return await message.err("`Wrong syntax`\nNo arguements", del_in=5)

    found = await SNIPS.find_one_and_delete({'snip_name': snip_name})

    if found:

        await message.edit(f"Snip <b>${found['snip_name']}</b> deleted successfully !", del_in=5, log=__name__)

    else:

        await message.err(f"Snip <b>${snip_name}<b> doesn\'t exist ! task failed successfully !", del_in=5)
