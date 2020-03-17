from . import get_all_plugins
from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("all", about="to get all plugins")
async def getplugins(_, message):
    all_plugins = await get_all_plugins()
    out_str = "**All Userge Plugins**\n\n"
    for plugin in all_plugins:
        out_str += f"**{plugin}**\n"
    await message.edit(out_str)