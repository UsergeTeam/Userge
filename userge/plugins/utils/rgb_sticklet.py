import os
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont
from userge import userge, Message


@userge.on_cmd("plet", about={
    'header': "Get a Random RGB Sticker",
    'description': "Generates A RGB Sticker with provided text",
    'usage': "{tr}plet [text | reply]",
    'examples': "{tr}plet @theUserge"})
async def sticklet(message: Message):
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

    font_file = await get_font_file()
    font = ImageFont.truetype(font_file, size=fontsize)

    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(font_file, size=fontsize)

    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(
        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B))

    image_name = "rgb_sticklet.webp"
    image.save(image_name, "WebP")

    await userge.send_sticker(
        chat_id=message.chat.id, sticker=image_name, reply_to_message_id=reply_to)

    # cleanup
    try:
        os.remove(font_file)
        os.remove(image_name)
    except Exception:
        pass


async def get_font_file():
    font_file_message_s = await userge.get_history("@FontsRes")
    font_file_message = random.choice(font_file_message_s)
    return await userge.download_media(font_file_message)
