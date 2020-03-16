from Userge import userge, logging, CMD_HELP

log = logging.getLogger(__name__)

from pyrogram import Filters, Message


@userge.on_message(Filters.command("help", ".") & Filters.me)
async def helpme(_, message: Message):
    out_str = ""
    for cmd in CMD_HELP:
        out_str += f".{cmd} : {CMD_HELP[cmd]}\n"
    await message.edit(out_str)


CMD_HELP.update({
    "help": "to know how to use this"
})
