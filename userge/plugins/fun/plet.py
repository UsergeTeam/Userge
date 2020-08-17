import io

import textwrap

from userge import userge, Message

from PIL import Image, ImageColor, ImageDraw, ImageFont

#from ubot.micro_bot import ldr

@userge.on_cmd("slet", about={

    'header': "Get a Sticker",

    'description': "Generates Sticker with provided text",

    'usage': "{tr}slet [text | reply]",

    'examples': "{tr}slet DeadSun"}, allow_via_bot=False)

async def sticklet(message: Message):

    # R = random.randint(0, 256)

    # G = random.randint(0, 256)

    # B = random.randint(0, 256)

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

    sticktext = find_optimal_wrap(sticktext)

    sticktext = '\n'.join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))

    draw = ImageDraw.Draw(image)

    fontsize = 230

    font = ImageFont.truetype("resources/Roboto-Regular.ttf", size=fontsize)

    while True:

        current_size = draw.multiline_textsize(sticktext, font=font, stroke_width=6, spacing=-10)

        if current_size[0] > 512 or current_size[1] > 512-64:

            fontsize -= 3

            font = ImageFont.truetype("resources/Roboto-Regular.ttf", size=fontsize)

        else:

            break

    width, height = draw.multiline_textsize(sticktext, font=font, stroke_width=6, spacing=-10)

    image = Image.new("RGBA", (512, height+64), (255, 255, 255, 0))

    draw = ImageDraw.Draw(image)

    draw.multiline_text((int((512 - width) / 2), 0), sticktext, font=font, fill="white", stroke_width=6, stroke_fill="black", spacing=-10)

    bbox = image.getbbox()

    image = image.crop((0, bbox[1], 512, bbox[3]))

    image_name = io.BytesIO()

    image_name.name = "sticker.webp"

    image.save(image_name, "WebP")

    image_name.seek(0)

    await userge.send_sticker(

        chat_id=message.chat.id, sticker=image_name, reply_to_message_id=reply_to)

    # cleanup

    try:

        os.remove(font_file)

        os.remove(image_name)

    except Exception:

        pass

def find_optimal_wrap(text):

    chicken_wrap = int(len(text) / 18) or 20

    wrapped_text = textwrap.wrap(text, width=chicken_wrap)

    while len(wrapped_text)*3 > chicken_wrap:

        chicken_wrap += 1

        wrapped_text = textwrap.wrap(text, width=chicken_wrap)

    return wrapped_text

