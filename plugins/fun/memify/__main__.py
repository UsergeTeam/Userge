""" memify """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os
import textwrap

from PIL import Image, ImageFont, ImageDraw

from userge import userge, Message, config
from userge.utils import progress, take_screen_shot, runcmd


@userge.on_cmd("mmf", about={
    'header': "Memify aka Geyify (๑¯ω¯๑)",
    'description': "Write text on any gif/sticker/image. "
                   "Top and bottom text are separated by ; \n Naw gu Awey",
    'usage': "{tr}mmf [text on top] ; [text on bottom] as a reply.",
    'examples': "Gwad who needs examples for this"})
async def memify(message: Message):
    replied = message.reply_to_message
    if not replied:
        await message.err("LMAO no one's gonna help you, if u use .help now then u **Gey**")
        await message.client.send_sticker(
            sticker="CAADAQADhAAD3gkwRviGxMVn5813FgQ", chat_id=message.chat.id)
        return
    if not (replied.photo or replied.sticker or replied.animation):
        await message.err("Bruh, U Comedy me? Read help or gtfo (¬_¬)")
        return
    if not os.path.isdir(config.Dynamic.DOWN_PATH):
        os.makedirs(config.Dynamic.DOWN_PATH)
    await message.edit("He he, let me use my skills")
    dls = await message.client.download_media(
        message=message.reply_to_message,
        file_name=config.Dynamic.DOWN_PATH,
        progress=progress,
        progress_args=(message, "Trying to Posses given content")
    )
    dls_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(dls))
    if replied.sticker and replied.sticker.file_name.endswith(".tgs"):
        await message.edit("OMG, an Animated sticker ⊙_⊙, lemme do my bleck megik...")
        png_file = os.path.join(config.Dynamic.DOWN_PATH, "meme.png")
        cmd = f"lottie_convert.py --frame 0 -if lottie -of png {dls_loc} {png_file}"
        stdout, stderr = (await runcmd(cmd))[:2]
        os.remove(dls_loc)
        if not os.path.lexists(png_file):
            await message.err("This sticker is Gey, i won't memify it ≧ω≦")
            raise Exception(stdout + stderr)
        dls_loc = png_file
    elif replied.animation:
        await message.edit("Look it's GF. Oh, no it's just a Gif ")
        jpg_file = os.path.join(config.Dynamic.DOWN_PATH, "meme.jpg")
        await take_screen_shot(dls_loc, 0, jpg_file)
        os.remove(dls_loc)
        if not os.path.lexists(jpg_file):
            await message.err("This Gif is Gey (｡ì _ í｡), won't memify it.")
            return
        dls_loc = jpg_file
    await message.edit("Decoration Time ≧∇≦, I'm an Artist")
    webp_file = await draw_meme_text(dls_loc, message.input_str)
    await message.client.send_sticker(chat_id=message.chat.id,
                                      sticker=webp_file,
                                      reply_to_message_id=replied.message_id)
    await message.delete()
    os.remove(webp_file)


async def draw_meme_text(image_path, text):
    img = Image.open(image_path)
    os.remove(image_path)
    i_width, i_height = img.size
    m_font = ImageFont.truetype(
        "userge/plugins/fun/memify/resources/MutantAcademyStyle.ttf",
        int((70 / 640) * i_width)
    )
    if ";" in text:
        upper_text, lower_text = text.split(";")
    else:
        upper_text = text
        lower_text = ''
    draw = ImageDraw.Draw(img)
    current_h, pad = 10, 5
    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(xy=(((i_width - u_width) / 2) - 1, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2) + 1, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=((i_width - u_width) / 2, int(((current_h / 640)*i_width)) - 1),
                      text=u_text, font=m_font, fill=(0, 0, 0))
            draw.text(xy=(((i_width - u_width) / 2), int(((current_h / 640)*i_width)) + 1),
                      text=u_text, font=m_font, fill=(0, 0, 0))

            draw.text(xy=((i_width - u_width) / 2, int((current_h / 640)*i_width)),
                      text=u_text, font=m_font, fill=(255, 255, 255))
            current_h += u_height + pad
    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(
                xy=(((i_width - u_width) / 2) - 1, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(
                xy=(((i_width - u_width) / 2) + 1, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(
                xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640)*i_width)) - 1),
                text=l_text, font=m_font, fill=(0, 0, 0))
            draw.text(
                xy=((i_width - u_width) / 2, (i_height - u_height - int((20 / 640)*i_width)) + 1),
                text=l_text, font=m_font, fill=(0, 0, 0))

            draw.text(
                xy=((i_width - u_width) / 2, i_height - u_height - int((20 / 640)*i_width)),
                text=l_text, font=m_font, fill=(255, 255, 255))
            current_h += u_height + pad

    image_name = "memify.webp"
    webp_file = os.path.join(config.Dynamic.DOWN_PATH, image_name)
    img.save(webp_file, "WebP")
    return webp_file
