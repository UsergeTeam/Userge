
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
    # PROCESS_RUN_TIME = 100 # what is this, I do not know
    input_str = message.matches[0].group(1).lower()
    selected_transfer = message.matches[0].group(2)
    if input_str:
        file_name = input_str
    else:
        # this is not pyro Shoot. I thought I checked all these modules
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
            file_name)  # this goes to there
    except KeyError:
        await message.err("Invalid selected Transfer")
        return
    cmd = selected_one
    # start_time = time.time() + PROCESS_RUN_TIME # Got it, not used or maybe for progress?
    # I have no idea about below lines

    # process = await asyncio.create_subprocess_shell(
    #    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    # )  # this one execute any linux command it subprocess,
    # stdout, stderr = await process.communicate()  # this is the out put
    # await message.edit(f"{stdout.decode()}")  # lets check now, yep
    response = subprocess.check_output(shlex.split(cmd))
    links = '\n'.join(re.findall(r'https?://[^\"\']+', response.decode()))
    print(response, links)
    await message.edit(f"I found these links :\n{links}")
# weren't you checking python2.x docs?
