# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, Config


@userge.on_cmd("help", about={'header': "Guide to use USERGE commands"})
async def helpme(message: Message) -> None:
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = f"""**--Which plugin you want ?--**

**Usage**:

    `{Config.CMD_TRIGGER}help [plugin_name]`

**Hint**:

    use `{Config.CMD_TRIGGER}s` for search commands.
    ex: `{Config.CMD_TRIGGER}s wel`

**({len(plugins)}) Plugins Available:**\n\n"""
        for i in sorted(plugins):
            out_str += f"`{i}`    "
    else:
        key = message.input_str
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in plugins
                and (len(plugins[key].enabled_commands) > 1
                     or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER) != key)):
            commands = plugins[key].get_commands()
            out_str = f"""**--Which command you want ?--**

**Usage**:

    `{Config.CMD_TRIGGER}help [command_name | command_name_with_prefix]`

**Hint**:

    use `{Config.CMD_TRIGGER}s` for search commands.
    ex: `{Config.CMD_TRIGGER}s wel`

**({len(commands)}) Commands Available Under `{key}` Plugin:**\n\n"""
            for i in commands:
                out_str += f"`{i}`    "
        else:
            commands = userge.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"`{key}`\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"`{key_}`\n\n{commands[key_].about}"
            else:
                out_str = f"__No Module or Command Found for__: `{message.input_str}`"
    await message.edit(text=out_str, del_in=0)
