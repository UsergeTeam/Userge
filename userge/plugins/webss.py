from userge import userge, Message, Config
import requests
from time import time
import os


@userge.on_cmd("webss", about="__Get snapshot of a website__")
async def webss(message: Message):
    if Config.SCREENSHOT_API is None:
        await message.edit("Damn!\nI forgot to get the api from (here)[https://screenshotlayer.com]", del_in=10)
        return
    await message.edit("`Processing`")
    suc, data = await getimg(message.input_str)
    if suc:
        await message.edit('Uploading..')
        await userge.send_chat_action(message.chat.id, "upload_photo")
        await userge.send_document(message.chat.id, data, caption=message.input_str)
        await message.delete()
        await userge.send_chat_action(message.chat.id, "cancel")
        if os.path.isfile(data):
            os.remove(data)
    else:
        await message.err(data, del_in=6)


async def getimg(url):
    requrl = "https://api.screenshotlayer.com/api/capture"
    requrl += "?access_key={}&url={}&fullpage={}&viewport={}"
    response = requests.get(
        requrl.format(Config.SCREENSHOT_API, url, '1', "2560x1440"),
        stream=True
    )
    if 'image' in response.headers["content-type"]:
        fname = f"screenshot_{time()}.png"
        with open(fname, "wb") as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        return True, fname
    else:
        return False, response.text
