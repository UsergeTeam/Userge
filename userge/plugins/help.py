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
        out_str = f"""⚒ **--(`{len(plugins)}`) Plugins Available--**\n\n"""
        cat_plugins = userge.manager.get_plugins()
        for cat in sorted(cat_plugins):
            out_str += (f"    ✪ **{cat}** :   `"
                        + "`    `".join(sorted(cat_plugins[cat])) + "`\n\n")
        out_str += f"""📕 **Usage:**  `{Config.CMD_TRIGGER}help [plugin_name]`"""
    else:
        key = message.input_str
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in plugins
                and (len(plugins[key].enabled_commands) > 1
                     or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER) != key)):
            commands = plugins[key].get_commands()
            out_str = f"""⚔ **--(`{len(commands)}`) Commands Available--**

🔧 **Plugin:**  `{key}`\n\n"""
            for i in commands:
                out_str += f"    〔 `{i}` 〕\n"
            out_str += f"""\n📕 **Usage:**  `{Config.CMD_TRIGGER}help [command_name]`"""
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
    await message.edit(out_str, del_in=0)
