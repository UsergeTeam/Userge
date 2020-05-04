# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, Config


@userge.on_cmd("help", about={'header': "Guide to use USERGE commands"})
async def helpme(message: Message):
    out, is_mdl_or_key = userge.get_help(message.input_str)
    cmd = message.input_str
    if not out:
        out_str = "__No Module or Command Found!__"
    elif isinstance(out, str):
        out_str = f"`{is_mdl_or_key}`\n\n{out}"
    elif isinstance(out, list) and is_mdl_or_key:
        out_str = f"""**--Which module you want ?--**

**Usage**:

    `{Config.CMD_TRIGGER}help [module_name]`

**Hint**:

    use `{Config.CMD_TRIGGER}s` for search commands.
    ex: `{Config.CMD_TRIGGER}s wel`

**({len(out)}) Modules Available:**\n\n"""
        for i in out:
            out_str += f"`{i}`    "
    elif isinstance(out, list) and not is_mdl_or_key:
        out_str = f"""**--Which command you want ?--**

**Usage**:

    `{Config.CMD_TRIGGER}help [command_name | command_name_with_prefix]`

**Hint**:

    use `{Config.CMD_TRIGGER}s` for search commands.
    ex: `{Config.CMD_TRIGGER}s wel`

**({len(out)}) Commands Available Under `{cmd}` Module:**\n\n"""
        for i in out:
            out_str += f"`{i}`    "
    await message.edit(text=out_str, del_in=0)
