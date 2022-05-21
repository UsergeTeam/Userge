""" create random rgb sticker """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont

from userge import userge, Message, get_collection

PLET_FONT = get_collection("PLET_FONT")
FONTS_FILE_CHANNEL = "@FontsRes"
DEFAULT_FONTS = [120, 127, 121, 124, 122, 123]


@userge.on_start
async def init():
    global FONTS_FILE_CHANNEL  # pylint: disable=global-statement
    data = await PLET_FONT.find_one({"id": "PLET_FONT_CHANNEL"})
    if data:
        FONTS_FILE_CHANNEL = data["name"]


@userge.on_cmd("plet", about={
    'header': "Get a Random RGB Sticker",
    'description': "Generates A RGB Sticker with provided text",
    'flags': {'-c': "change fonts channel"},
    'usage': "{tr}plet [text | reply]",
    'examples': "{tr}plet @theUserge"})
async def sticklet(message: Message):
    global FONTS_FILE_CHANNEL  # pylint: disable=global-statement
    if message.flags and '-c' in message.flags and not message.client.is_bot:
        u = message.flags.get('-c')
        if not u:
            return await message.err("Channel Username not found!")
        try:
            await userge.resolve_peer(u)
        except Exception as err:
            await message.err(str(err))
        else:
            FONTS_FILE_CHANNEL = u
            await PLET_FONT.update_one({"id": "PLET_FONT_CHANNEL"},
                                       {"$set": {"name": u}},
                                       upsert=True)
            await message.edit("`Fonts channel saved successfully...`")
        return
    R = random.randint(0, 256)
    G = random.randint(0, 256)
    B = random.randint(0, 256)

    sticktext = message.input_or_reply_str
    if not sticktext:
        await message.edit("**Bruh** ~`I need some text to make sticklet`")
        return
    await message.delete()

    if message.reply_to_message:
        reply_to = message.reply_to_message.message_id
    else:
        reply_to = message.message_id

    # https://docs.python.org/3/library/textwrap.html#textwrap.wrap

    sticktext = textwrap.wrap(sticktext, width=10)
    sticktext = '\n'.join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230

    font_file = await get_font_file(message)
    try:
        font = ImageFont.truetype(font_file, size=fontsize)
    except Exception:
        return await message.err("I guess your channel conatins invalid font files!")

    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(font_file, size=fontsize)

    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(
        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B))

    image_name = "rgb_sticklet.webp"
    image.save(image_name, "WebP")

    await message.client.send_sticker(
        chat_id=message.chat.id, sticker=image_name, reply_to_message_id=reply_to)

    # cleanup
    try:
        os.remove(font_file)
        os.remove(image_name)
    except Exception:
        pass


async def get_font_file(message):
    if message.client.is_bot:
        font_file_message_s = await message.client.get_messages(
            FONTS_FILE_CHANNEL, DEFAULT_FONTS)
        font_file_message = random.choice(font_file_message_s)
    else:
        font_file_message_s = await message.client.get_history(FONTS_FILE_CHANNEL)
        font_file_message = random.choice(font_file_message_s)
    return await font_file_message.download()
