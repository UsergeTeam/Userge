# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from userge import userge, Message, Config, versions


@userge.on_cmd("repo", about="__get repo link and details__")
async def see_repo(message: Message):
    """see repo"""

    output = f"""
**Hey**, __I am using__ 🥳 [Userge]({Config.UPSTREAM_REPO}) 😎

• **userge version** : `{versions.__version__}`
• **license** : {versions.__license__}
• **copyright** : {versions.__copyright__}
"""

    await message.edit(output, disable_web_page_preview=True)
