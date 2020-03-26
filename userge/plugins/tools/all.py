from userge import userge, Message
from .. import get_all_plugins


@userge.on_cmd("all", about="__list all plugins in plugins/ path__")
async def getplugins(message: Message):
    all_plugins = ['/'.join(i.split('.')) for i in get_all_plugins()]

    out_str = "**--All Userge Plugins--**\n\n"

    for plugin in all_plugins:
        out_str += f"    `{plugin}.py`\n"

    await message.edit(text=out_str, del_in=15)
