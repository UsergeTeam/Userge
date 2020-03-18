import os
from datetime import datetime
from . import get_all_plugins
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("ping", about="check how long it takes to ping your userbot")
async def pingme(_, message):
    start = datetime.now()

    await message.edit('`Pong!`')

    end = datetime.now()
    ms = (end - start).microseconds / 1000

    await message.edit(f"**Pong!**\n`{ms} ms`")


@userge.on_cmd("help", about="to know how to use this")
async def helpme(_, message):
    out_str = ""

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]

    except:
        out_str += "**which command you want ?**\n\n"

        for cmd in sorted(userge.get_help()):
            out_str += f"**.{cmd}**\n"

    else:
        out = userge.get_help(cmd)
        out_str += f"**.{cmd}**\n\n__{out}__" if out else "__command not found!__"

    await message.edit(out_str)


@userge.on_cmd("json", about="replied msg to json")
async def jsonify(_, message):
    the_real_message = None
    reply_to_id =  None

    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
        the_real_message = message.reply_to_message

    else:
        the_real_message = message
        reply_to_id = message.message_id

    try:
        await message.edit(the_real_message)

    except Exception as e:
        with open("json.text", "w+", encoding="utf8") as out_file:
            out_file.write(str(the_real_message))
        await userge.send_document(
            chat_id=message.chat.id,
            document="json.text",
            caption=str(e),
            disable_notification=True,
            reply_to_message_id=reply_to_id
        )

        os.remove("json.text")
        await message.delete()


@userge.on_cmd("all", about="to get all plugins")
async def getplugins(_, message):
    all_plugins = await get_all_plugins()

    out_str = "**All Userge Plugins**\n\n"

    for plugin in all_plugins:
        out_str += f"**{plugin}**\n"
        
    await message.edit(out_str)


@userge.on_cmd("del", about="to delete replied msg")
async def del_msg(_, message):
    msg_ids = [message.message_id]

    if message.reply_to_message:
        msg_ids.append(message.reply_to_message.message_id)

    await userge.delete_messages(message.chat.id, msg_ids)