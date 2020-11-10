""" kang stickers """

# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import os
import random
import emoji

from PIL import Image
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName
from pyrogram.errors import YouBlockedUser, StickersetInvalid

from userge import userge, Message, Config


@userge.on_cmd(
    "kang", about={
        'header': "kangs stickers or creates new ones",
        'flags': {
            '-s': "without link",
            '-d': "without trace"},
        'usage': "Reply {tr}kang [emoji('s)] [pack number] to a sticker or "
                 "an image to kang it to your userbot pack.",
        'examples': ["{tr}kang", "{tr}kang -s", "{tr}kang -d",
                     "{tr}kang 🤔", "{tr}kang 2", "{tr}kang 🤔 2"]},
    allow_channels=False, allow_via_bot=False)
async def kang_(message: Message):
    """ kang a sticker """
    user = await userge.get_me()
    replied = message.reply_to_message
    photo = None
    emoji_ = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`Sticker has no Name!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith('.tgs'):
                resize = True
        else:
            await message.edit("`Unsupported File!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await userge.download_media(message=replied,
                                            file_name=Config.DOWN_PATH)
    else:
        await message.edit("`I can't kang that...`")
        return
    if photo:
        args = message.filtered_input_str.split()
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in emoji.UNICODE_EMOJI:
            emoji_ = None
        if not emoji_:
            emoji_ = "🤔"

        u_name = user.username
        if u_name:
            u_name = "@" + u_name
        else:
            u_name = user.first_name or user.id
        packname = f"a{user.id}_by_userge_{pack}"
        custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s kang pack"
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = '/newpack'
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = '/newanimated'
        exist = False
        try:
            exist = await message.client.send(
                GetStickerSet(
                    stickerset=InputStickerSetShortName(
                        short_name=packname)))
        except StickersetInvalid:
            pass
        if exist is not False:
            async with userge.conversation('Stickers', limit=30) as conv:
                try:
                    await conv.send_message('/addsticker')
                except YouBlockedUser:
                    await message.edit('first **unblock** @Stickers')
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                limit = "50" if is_anim else "120"
                while limit in msg.text:
                    pack += 1
                    packname = f"a{user.id}_by_userge_{pack}"
                    packnick = f"{custom_packnick} Vol.{pack}"
                    if is_anim:
                        packname += "_anim"
                        packnick += " (Animated)"
                    await message.edit("`Switching to Pack " + str(pack) +
                                       " due to insufficient space`")
                    await conv.send_message(packname)
                    msg = await conv.get_response(mark_read=True)
                    if msg.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packnick)
                        await conv.get_response(mark_read=True)
                        await conv.send_document(photo)
                        await conv.get_response(mark_read=True)
                        await conv.send_message(emoji_)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response(mark_read=True)
                            await conv.send_message(f"<{packnick}>", parse_mode=None)
                        await conv.get_response(mark_read=True)
                        await conv.send_message("/skip")
                        await conv.get_response(mark_read=True)
                        await conv.send_message(packname)
                        await conv.get_response(mark_read=True)
                        if '-d' in message.flags:
                            await message.delete()
                        else:
                            out = "__kanged__" if '-s' in message.flags else \
                                f"[kanged](t.me/addstickers/{packname})"
                            await message.edit(f"**Sticker** {out} __in a Different Pack__**!**")
                        return
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await message.edit("`Failed to add sticker, use` @Stickers "
                                       "`bot to add the sticker manually.`")
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message('/done')
                await conv.get_response(mark_read=True)
        else:
            await message.edit("`Brewing a new Pack...`")
            async with userge.conversation('Stickers') as conv:
                try:
                    await conv.send_message(cmd)
                except YouBlockedUser:
                    await message.edit('first **unblock** @Stickers')
                    return
                await conv.get_response(mark_read=True)
                await conv.send_message(packnick)
                await conv.get_response(mark_read=True)
                await conv.send_document(photo)
                rsp = await conv.get_response(mark_read=True)
                if "Sorry, the file type is invalid." in rsp.text:
                    await message.edit("`Failed to add sticker, use` @Stickers "
                                       "`bot to add the sticker manually.`")
                    return
                await conv.send_message(emoji_)
                await conv.get_response(mark_read=True)
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response(mark_read=True)
                    await conv.send_message(f"<{packnick}>", parse_mode=None)
                await conv.get_response(mark_read=True)
                await conv.send_message("/skip")
                await conv.get_response(mark_read=True)
                await conv.send_message(packname)
                await conv.get_response(mark_read=True)
        if '-d' in message.flags:
            await message.delete()
        else:
            out = "__kanged__" if '-s' in message.flags else \
                f"[kanged](t.me/addstickers/{packname})"
            await message.edit(f"**Sticker** {out}**!**")
        if os.path.exists(str(photo)):
            os.remove(photo)


@userge.on_cmd("stkrinfo", about={
    'header': "get sticker pack info",
    'usage': "reply {tr}stkrinfo to any sticker"})
async def sticker_pack_info_(message: Message):
    """ get sticker pack info """
    replied = message.reply_to_message
    if not replied:
        await message.edit("`I can't fetch info from nothing, can I ?!`")
        return
    if not replied.sticker:
        await message.edit("`Reply to a sticker to get the pack details`")
        return
    await message.edit("`Fetching details of the sticker pack, please wait..`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(
                short_name=replied.sticker.set_name)))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = f"**Sticker Title:** `{get_stickerset.set.title}\n`" \
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n" \
        f"**Archived:** `{get_stickerset.set.archived}`\n" \
        f"**Official:** `{get_stickerset.set.official}`\n" \
        f"**Masks:** `{get_stickerset.set.masks}`\n" \
        f"**Animated:** `{get_stickerset.set.animated}`\n" \
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n" \
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    await message.edit(out_str)


def resize_photo(photo: str) -> io.BytesIO:
    """ Resize the given photo to 512x512 """
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width*scale), int(image.height*scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


KANGING_STR = (
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "hehe me stel ur stikér\nhehe.",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pacc looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal Your Sticker is stealing this sticker... ")
