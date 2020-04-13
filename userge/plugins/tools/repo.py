# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, Config


@userge.on_cmd("repo", about="__get repo link__")
async def getplugins(message: Message):
    await message.edit(f"**Hey**, __I am using__ 🥳 [Userge]({Config.OFFICIAL_REPO_LINK}) 😎")
