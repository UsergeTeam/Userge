# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import re
import shlex
import time
import asyncio

from userge import userge, Message, Config
from userge.utils import progress


@userge.on_cmd("web ?(.+?|) (anonfiles|transfer|filebin|anonymousfiles|megaupload|bayfiles)",
               about={
                   'header': "upload files to web",
                   'usage': "{tr}web [site name]",
                   'types': ['anonfiles', 'transfer', 'filebin', 'anonymousfiles', 'megaupload', 'bayfiles']})
async def web(message: Message):
    await message.edit("`Processing ...`")
    input_str = message.matches[0].group(1)
    selected_transfer = message.matches[0].group(2).lower()
    if input_str:
        file_name = input_str
    else:
        c_time = time.time()
        file_name = await userge.download_media(
            message=message.reply_to_message,
            file_name=Config.DOWN_PATH,
            progress=progress,
            progress_args=(
                "trying to download", userge, message, c_time
            )
        )
    hosts = {
        "anonfiles": "curl -F \"file=@{}\" https://anonfiles.com/api/upload",
        "transfer": "curl --upload-file \"{}\" https://transfer.sh/" + os.path.basename(file_name),
        "filebin": "curl -X POST --data-binary \"@test.png\" -H \"filename: {}\" \"https://filebin.net\"",
        "anonymousfiles": "curl -F file=\"@{}\" https://api.anonymousfiles.io/",
        "megaupload": "curl -F \"file=@{}\" https://megaupload.is/api/upload",
        "bayfiles": "curl -F \"file=@{}\" https://api.bayfiles.com/upload"
    }
    try:
        cmd = hosts[selected_transfer].format(file_name)
    except KeyError:
        await message.err("Invalid selected Transfer")
        return
    process = await asyncio.create_subprocess_exec(
       *shlex.split(cmd), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    response, _ = await process.communicate()
    links = '\n'.join(re.findall(r'https?://[^\"\']+', response.decode()))
    await message.edit(f"I found these links :\n{links}")
