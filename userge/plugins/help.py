# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message, Config

_CATEGORY = {
    'admin': '👨‍✈️',
    'fun': '🎨',
    'misc': '⚙️',
    'tools': '🧰',
    'utils': '🗂',
    'unofficial': '🃏',
    'temp': '♻️',
    'plugins': '💎'
}


@userge.on_cmd("help", about={'header': "Guide to use USERGE commands"}, allow_channels=False)
async def helpme(message: Message) -> None:  # pylint: disable=missing-function-docstring
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = f"""⚒ <b><u>(<code>{len(plugins)}</code>) Plugins Available</u></b>\n\n"""
        cat_plugins = userge.manager.get_plugins()
        for cat in sorted(cat_plugins):
            out_str += (f"    {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                        f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                        + "</code>    <code>".join(sorted(cat_plugins[cat])) + "</code>\n\n")
        out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [plugin_name]</code>"""
    else:
        key = message.input_str
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in plugins
                and (len(plugins[key].enabled_commands) > 1
                     or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER) != key)):
            commands = plugins[key].enabled_commands
            out_str = f"""⚔ <b><u>(<code>{len(commands)}</code>) Commands Available</u></b>

🔧 <b>Plugin:</b>  <code>{key}</code>
📘 <b>About:</b>  <code>{plugins[key].about}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (f"    🤖 <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                            f"    📚 <b>info:</b>  <i>{cmd.doc}</i>\n\n")
            out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [command_name]</code>"""
        else:
            commands = userge.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>No Module or Command Found for</i>: <code>{message.input_str}</code>"
    await message.edit(out_str, del_in=0, parse_mode='html')
