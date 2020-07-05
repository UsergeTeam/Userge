# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

import requests

from userge import userge, Message, Config, pool

CHANNEL = userge.getCLogger(__name__)


@pool.run_in_thread
def ocr_space_file(filename,
                   language='eng',
                   overlay=False,
                   api_key=Config.OCR_SPACE_API_KEY):
    """
    OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
    }
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data=payload,
        )
    return r.json()


@userge.on_cmd("ocr", about={
    'header': "use this to run ocr reader",
    'description': "get ocr result for images (file size limit = 1MB)",
    'examples': [
        "{tr}ocr [reply to image]",
        "{tr}ocr eng [reply to image] (get lang codes from 'https://ocr.space/ocrapi')"]})
async def ocr_gen(message: Message):
    """
    this function can generate ocr output for a image file
    """
    if Config.OCR_SPACE_API_KEY is None:
        await message.edit(
            "<code>Oops!!get the OCR API from</code> "
            "<a href='http://eepurl.com/bOLOcf'>HERE</a> "
            "<code>& add it to Heroku config vars</code> (<code>OCR_SPACE_API_KEY</code>)",
            disable_web_page_preview=True,
            parse_mode="html", del_in=0)
        return

    if message.reply_to_message:

        if message.input_str:
            lang_code = message.input_str
        else:
            lang_code = "eng"

        await message.edit(r"`Trying to Read.. 📖")
        downloaded_file_name = await message.client.download_media(message.reply_to_message)
        test_file = await ocr_space_file(downloaded_file_name, lang_code)
        try:
            ParsedText = test_file["ParsedResults"][0]["ParsedText"]
        except Exception as e_f:
            await message.edit(
                r"`Couldn't read it.. (╯‵□′)╯︵┻━┻`"
                "\n`I guess I need new glasses.. 👓`"
                f"\n\n**ERROR**: `{e_f}`", del_in=0)
            os.remove(downloaded_file_name)
            return
        else:
            await message.edit(
                "**Here's what I could read from it:**"
                f"\n\n`{ParsedText}`")
            os.remove(downloaded_file_name)
            await CHANNEL.log("`ocr` command succefully executed")
            return

    else:
        await message.edit(r"`i can't read nothing (°ー°〃) , do .help ocr`", del_in=0)
        return
