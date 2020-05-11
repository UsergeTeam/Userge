# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.
import os
import io
import re
import shlex
import time
import asyncio
import subprocess

from userge import userge, Message, Config


@userge.on_cmd("web ?(.+?|) (anonfiles|transfer|filebin|anonymousfiles|megaupload|bayfiles)",
               about={
                   'header': "upload files to web",
                   'usage': "{tr}web [site name]",
                   'types': ['anonfiles', 'transfer', 'filebin', 'anonymousfiles', 'megaupload', 'bayfiles']})
async def web(message: Message):
    await message.edit("Processing ...")
    input_str = message.matches[0].group(1).lower()
    selected_transfer = message.matches[0].group(2)
    if input_str:
        file_name = input_str
    else:
        reply = message.reply_to_message
        file_name = await userge.download_media(reply, Config.DOWN_PATH)
    reply_to_id = message.chat.id
    CMD_WEB = {
        "anonfiles": "curl -F \"file=@{}\" https://anonfiles.com/api/upload",
        "transfer": "curl --upload-file \"{}\" https://transfer.sh/" + os.path.basename(file_name),
        "filebin": "curl -X POST --data-binary \"@test.png\" -H \"filename: {}\" \"https://filebin.net\"",
        "anonymousfiles": "curl -F file=\"@{}\" https://api.anonymousfiles.io/",
        "megaupload": "curl -F \"file=@{}\" https://megaupload.is/api/upload",
        "bayfiles": "curl -F \"file=@{}\" https://api.bayfiles.com/upload"
    }
    try:
        selected_one = CMD_WEB[selected_transfer].format(
            file_name)
    except KeyError:
        await message.err("Invalid selected Transfer")
        return
    cmd = selected_one

    # process = await asyncio.create_subprocess_shell(
    #    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    # )
    # stdout, stderr = await process.communicate()
    # await message.edit(f"{stdout.decode()}")
    response = subprocess.check_output(shlex.split(cmd))
    links = '\n'.join(re.findall(r'https?://[^\"\']+', response.decode()))
    print(response, links)
    await message.edit(f"I found these links :\n{links}")
