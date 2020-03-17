from userge import userge

log = userge.getLogger(__name__)


@userge.on_cmd("help", about="to know how to use this")
async def helpme(_, message):
    out_str = ""
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except:
        out_str += "**which command you want ?**\n\n"
        for cmd in userge.get_help():
            out_str += f"**.{cmd}**\n"
    else:
        out = userge.get_help(cmd)
        out_str += f"**.{cmd}**\n\n__{out}__" if out else "__command not found!__"
    await message.edit(out_str)
