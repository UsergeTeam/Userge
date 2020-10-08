"""MEDIA INFO"""



import os

from userge.utils import runcmd, post_to_telegraph

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from userge import userge, Message

TYPES = ['audio', 'document', 'animation', 'video', 'voice', 'video_note', 'photo', 'sticker']

X_MEDIA = None

@userge.on_cmd("mediainfo", about={

    'header': "Get Detailed Info About Replied Media"})

async def mediainfo(message: Message):

    """Get Media Info"""

    reply = message.reply_to_message

    if not reply:

        await message.err('reply to media first', del_in=5)

        return

    process = await message.edit('`Processing ...`')

    for media_type in TYPES:

        if reply[media_type]:

            X_MEDIA = media_type

            break

    if not X_MEDIA:

        return await message.err('Reply To a Vaild Media Format', del_in=5)

    file_path = await reply.download()

    out, err, ret, pid = await runcmd(f"mediainfo {file_path}")

    if not out:

        out = "Not Supported"

    body_text = f"""<br>

<h2>JSON</h2>

<code>{reply[X_MEDIA]}</code>

<br>

<br>

<h2>DETAILS</h2>

<code>{out}</code>

"""

    link = post_to_telegraph(f'pyrogram.types.{X_MEDIA}', body_text)

    if message.client.is_bot:

        markup = InlineKeyboardMarkup([[

                        InlineKeyboardButton(text=X_MEDIA.upper(), url=link)

                        ]])

        await process.edit_text(

            "ℹ️  <b>MEDIA INFO</b>",

            reply_markup=markup

        )

    else:

        await message.edit(f'ℹ️  <b>MEDIA INFO:  [{X_MEDIA.upper()}]({link})</b>')

    os.remove(file_path)
