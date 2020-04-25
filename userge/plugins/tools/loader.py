# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os

from userge import userge, Message
from userge.utils import get_import_path
from userge.plugins import ROOT

TMP_PATH = "userge/plugins/temp/"


@userge.on_cmd('load', about={
    'header': "Load Userge plugin",
    'usage': ".load [reply to userge plugin]"})
async def load_cmd_handler(message: Message):
    await message.edit("Loading...")
    replied = message.reply_to_message
    if replied and replied.document:
        file_ = replied.document

        if file_.file_name.endswith('.py') and file_.file_size < 2 ** 20:
            if not os.path.isdir(TMP_PATH):
                os.makedirs(TMP_PATH)

            t_path = os.path.join(TMP_PATH, file_.file_name)
            if os.path.isfile(t_path):
                os.remove(t_path)

            await replied.download(file_name=t_path)
            plugin = get_import_path(ROOT, t_path)

            try:
                userge.load_plugin(plugin)

            except (ImportError, SyntaxError) as i_e:
                os.remove(t_path)
                await message.err(i_e)

            else:
                await message.edit(f"`Loaded {plugin}`", del_in=3, log=__name__)

        else:
            await message.edit("`Plugin Not Found`")

    else:
        await message.edit("`Reply to Plugin`")


@userge.on_cmd('reload', about={'header': "Reload all plugins"})
async def reload_cmd_handler(message: Message):
    await message.edit("`Reloading All Plugins`")

    await message.edit(
        f"`Reloaded {await userge.reload_plugins()} Plugins`", del_in=3, log=__name__)
