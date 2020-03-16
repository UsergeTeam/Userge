from pyrogram import Message
from . import get_all_plugins
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("all")
async def getplugins(_, message: Message):
    all_plugins = await get_all_plugins()
    out_str = ""
    for plugin in all_plugins:
        out_str += f"{plugin}.py\n"
    await message.edit(out_str)


userge.add_help(
    command="all",
    about="to get all plugins"
)