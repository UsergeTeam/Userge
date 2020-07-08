# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import random
import asyncio
from urllib.parse import quote_plus

import aiofiles
from selenium import webdriver
from pyrogram.errors.exceptions.bad_request_400 import YouBlockedUser

from userge import userge, Message, Config

CARBON = 'https://carbon.now.sh/?t={theme}&l={lang}&code={code}&bg={bg}'


@userge.on_cmd("carbon", about={
    'header': "create a carbon",
    'flags': {
        '-r': "red -> 0-255",
        '-g': "green -> 0-255",
        '-b': "blue -> 0-255",
        '-a': "alpha -> 0-100"},
    'usage': "{tr}carbon [flags] [theme] | [language] | [text | reply to msg]",
    'examples': [
        "{tr}carbon haha", "{tr}carbon vscode | hoho",
        "{tr}carbon -r100 -g75 -b50 -a50 blackboard | hola"],
    'themes': [
        '3024-night', 'a11y-dark', 'blackboard', 'base16-dark', 'base16-light',
        'cobalt', 'dracula', 'duotone-dark', 'hopscotch', 'lucario', 'material',
        'monokai', 'night-owl', 'nord', 'oceanic-next', 'one-light', 'one-dark',
        'panda-syntax', 'paraiso-dark', 'seti', 'shades-of-purple', 'solarized dark',
        'solarized light', 'synthwave-84', 'twilight', 'verminal', 'vscode',
        'yeti', 'zenburn']}, del_pre=True)
async def carbon_(message: Message):
    if Config.GOOGLE_CHROME_BIN is None:
        replied = message.reply_to_message
        if replied:
            text = replied.text
        else:
            text = message.text
        if not text:
            await message.err("need input text!")
            return
        await message.edit("`Creating a Carbon...`")
        async with userge.conversation("CarbonNowShBot", timeout=30) as conv:
            try:
                await conv.send_message(text)
            except YouBlockedUser:
                await message.edit('first **unblock** @CarbonNowShBot')
                return
            response = await conv.get_response(mark_read=True)
            while not response.reply_markup:
                response = await conv.get_response(mark_read=True)
            await response.click(x=random.randint(0, 2), y=random.randint(0, 8))
            response = await conv.get_response(mark_read=True)
            while not response.media:
                response = await conv.get_response(mark_read=True)
            caption = "\n".join(response.caption.split("\n")[0:2])
            file_id = response.document.file_id
            await asyncio.gather(
                message.delete(),
                userge.send_document(chat_id=message.chat.id,
                                     document=file_id,
                                     caption='`' + caption + '`',
                                     reply_to_message_id=replied.message_id if replied else None)
            )
    else:
        input_str = message.filtered_input_str
        replied = message.reply_to_message
        theme = 'seti'
        lang = 'auto'
        red = message.flags.get('r', random.randint(0, 255))
        green = message.flags.get('g', random.randint(0, 255))
        blue = message.flags.get('b', random.randint(0, 255))
        alpha = message.flags.get('a', random.randint(0, 100))
        bg_ = f"rgba({red}, {green}, {blue}, {alpha})"
        if replied and (replied.text
                        or (replied.document and 'text' in replied.document.mime_type)):
            message_id = replied.message_id
            if replied.document:
                await message.edit("`Downloading File...`")
                path_ = await message.client.download_media(replied, file_name=Config.DOWN_PATH)
                async with aiofiles.open(path_) as file_:
                    code = await file_.read()
                os.remove(path_)
            else:
                code = replied.text
            if input_str:
                if '|' in input_str:
                    args = input_str.split('|')
                    if len(args) == 2:
                        theme = args[0].strip()
                        lang = args[1].strip()
                else:
                    theme = input_str
        elif input_str:
            message_id = message.message_id
            if '|' in input_str:
                args = input_str.split('|')
                if len(args) == 3:
                    theme = args[0].strip()
                    lang = args[1].strip()
                    code = args[2].strip()
                elif len(args) == 2:
                    theme = args[0].strip()
                    code = args[1].strip()
            else:
                code = input_str
        else:
            await message.err("need input text!")
            return
        await message.edit("`Creating a Carbon...`")
        code = quote_plus(code)
        await message.edit("`Processing... 20%`")
        carbon_path = os.path.join(Config.DOWN_PATH, "carbon.png")
        if os.path.isfile(carbon_path):
            os.remove(carbon_path)
        url = CARBON.format(theme=theme, lang=lang, code=code, bg=bg_)
        if len(url) > 2590:
            await message.err("input too large!")
            return
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = Config.GOOGLE_CHROME_BIN
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        prefs = {'download.default_directory': Config.DOWN_PATH}
        chrome_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        await message.edit("`Processing... 40%`")
        driver.command_executor._commands["send_command"] = (  # pylint: disable=protected-access
            "POST", '/session/$sessionId/chromium/send_command')
        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': Config.DOWN_PATH
            }
        }
        driver.execute("send_command", params)
        # driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
        driver.find_element_by_id("export-menu").click()
        await asyncio.sleep(1)
        await message.edit("`Processing... 60%`")
        driver.find_element_by_xpath("//button[contains(text(),'4x')]").click()
        await asyncio.sleep(1)
        driver.find_element_by_xpath("//button[contains(text(),'PNG')]").click()
        await message.edit("`Processing... 80%`")
        while not os.path.isfile(carbon_path):
            await asyncio.sleep(0.5)
        await message.edit("`Processing... 100%`")
        await message.edit("`Uploading Carbon...`")
        await asyncio.gather(
            message.delete(),
            message.client.send_photo(chat_id=message.chat.id,
                                      photo=carbon_path,
                                      reply_to_message_id=message_id)
        )
        os.remove(carbon_path)
        driver.quit()
