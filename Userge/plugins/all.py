from Userge import userge, logging, CMD_HELP

log = logging.getLogger(__name__)


from pyrogram import Filters, Message
from . import get_all_plugins

@userge.on_message(Filters.command("all", ".") & Filters.me)
async def getplugins(_, message: Message):
    all_plugins = await get_all_plugins()
    out_str = ""
    for plugin in all_plugins:
        out_str += f"{plugin}.py\n"
    await message.edit(out_str)


CMD_HELP.update({
    "all": "to get all plugins"
})