from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("help", about="to know how to use this")
async def helpme(_, message):
    out_str = ""
    for cmd in userge.get_help():
        out_str += f"**.{cmd}** : __{userge.get_help(cmd)}__\n"
    await message.edit(out_str)
