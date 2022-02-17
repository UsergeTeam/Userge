""" kang stickers """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import io
import os
import random
from typing import Union

from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import emoji
from pyrogram.errors import YouBlockedUser, StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from userge import userge, Message, Config
from userge.utils.tools import runcmd


@userge.on_cmd(
    "kang", about={
        'header': "kangs stickers or creates new ones",
        'flags': {
            '-s': "without link",
            '-d': "without trace"},
        'usage': "Reply {tr}kang [emoji('s)] [pack number] to a sticker or "
                 "an image to kang it to your userbot pack.",
        'examples': ["{tr}kang", "{tr}kang -s", "{tr}kang -d",
                     "{tr}kang 🤔😎", "{tr}kang 2", "{tr}kang 🤔🤣😂 2"]},
    allow_channels=False, allow_via_bot=False)
async def kang_(message: Message):
    """ kang a sticker """
    replied = message.reply_to_message
    if not replied or not replied.media:
        return await message.err("`I can't kang that...`")

    emoji_ = ""
    is_anim = False
    is_video = False
    resize = False

    if replied.photo or replied.document and "image" in replied.document.mime_type:
        resize = True
    elif replied.document and "tgsticker" in replied.document.mime_type:
        is_anim = True
    elif replied.animation or (replied.document and "video" in replied.document.mime_type
                               and replied.document.file_size <= 10485760):
        resize = True
        is_video = True
    elif replied.sticker:
        if not replied.sticker.file_name:
            return await message.edit("`Sticker has no Name!`")
        _ = replied.sticker.emoji
        if _:
            emoji_ = _
        is_anim = replied.sticker.is_animated
        is_video = replied.sticker.is_video
        if not (
            replied.sticker.file_name.endswith('.tgs')
            or replied.sticker.file_name.endswith('.webm')
        ):
            resize = True
    else:
        return await message.edit("`Unsupported File!`")

    await message.edit(f"`{random.choice(KANGING_STR)}`")
    media = await userge.download_media(message=replied, file_name=Config.DOWN_PATH)
    if not media:
        return await message.edit("`No Media!`")

    args = message.filtered_input_str.split(' ')
    pack = 1
    _emoji = None

    if len(args) == 2:
        _emoji, pack = args
    elif len(args) == 1:
        if args[0].isnumeric():
            pack = int(args[0])
        else:
            _emoji = args[0]

    if _emoji is not None:
        _saved = emoji_
        for k in _emoji:
            if k and k in (
                getattr(emoji, a) for a in dir(emoji) if not a.startswith("_")
            ):
                emoji_ += k
        if _saved and _saved != emoji_:
            emoji_ = emoji_[len(_saved):]
    if not emoji_:
        emoji_ = "🤔"

    user = await userge.get_me()
    u_name = user.username
    if u_name:
        u_name = "@" + u_name
    else:
        u_name = user.first_name or user.id

    packname = f"a{user.id}_by_userge_{pack}"
    custom_packnick = Config.CUSTOM_PACK_NAME or f"{u_name}'s Kang Pack"
    packnick = f"{custom_packnick} Vol.{pack}"
    cmd = '/newpack'

    if resize:
        media = await resize_media(media, is_video)
    if is_anim:
        packname += "_anim"
        packnick += " (Animated)"
        cmd = '/newanimated'
    if is_video:
        packname += "_video"
        packnick += " (Video)"
        cmd = '/newvideo'

    exist = False
    try:
        exist = await message.client.send(
            GetStickerSet(
                stickerset=InputStickerSetShortName(
                    short_name=packname), hash=0))
    except StickersetInvalid:
        pass
    if exist is not False:
        async with userge.conversation('Stickers', limit=30) as conv:
            try:
                await conv.send_message('/addsticker')
            except YouBlockedUser:
                return await message.edit('first **unblock** @Stickers')
            await conv.get_response(mark_read=True)
            await conv.send_message(packname)
            msg = await conv.get_response(mark_read=True)
            limit = "50" if (is_anim or is_video) else "120"
            while limit in msg.text:
                pack += 1
                packname = f"a{user.id}_by_userge_{pack}"
                packnick = f"{custom_packnick} Vol.{pack}"
                if is_anim:
                    packname += "_anim"
                    packnick += " (Animated)"
                if is_video:
                    packname += "_video"
                    packnick += " (Video)"
                await message.edit(f"`Switching to Pack {pack} due to insufficient space`")
                await conv.send_message(packname)
                msg = await conv.get_response(mark_read=True)
                if msg.text == "Invalid pack selected.":
                    await conv.send_message(cmd)
                    await conv.get_response(mark_read=True)
                    await conv.send_message(packnick)
                    await conv.get_response(mark_read=True)
                    await conv.send_document(media)
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
            await conv.send_document(media)
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
                return await message.edit('first **unblock** @Stickers')
            await conv.get_response(mark_read=True)
            await conv.send_message(packnick)
            await conv.get_response(mark_read=True)
            await conv.send_document(media)
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
    if os.path.exists(str(media)):
        os.remove(media)


@userge.on_cmd("stkrinfo", about={
    'header': "get sticker pack info",
    'usage': "reply {tr}stkrinfo to any sticker"})
async def sticker_pack_info_(message: Message):
    """ get sticker pack info """
    replied = message.reply_to_message
    if not replied:
        await message.err("`I can't fetch info from nothing, can I ?!`")
        return
    if not replied.sticker:
        await message.err("`Reply to a sticker to get the pack details`")
        return
    await message.edit("`Fetching details of the sticker pack, please wait..`")
    get_stickerset = await message.client.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(
                short_name=replied.sticker.set_name), hash=0))
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = f"**Sticker Title:** `{get_stickerset.set.title}\n`" \
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n" \
        f"**Archived:** `{get_stickerset.set.archived}`\n" \
        f"**Official:** `{get_stickerset.set.official}`\n" \
        f"**Masks:** `{get_stickerset.set.masks}`\n" \
        f"**Video:** `{get_stickerset.set.gifs}`\n" \
        f"**Animated:** `{get_stickerset.set.animated}`\n" \
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n" \
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    await message.edit(out_str)


async def resize_media(media: str, video: bool) -> Union[str, io.BytesIO]:
    """ Resize the given media to 512x512 """
    if video:
        metadata = extractMetadata(createParser(media))
        width = round(metadata.get('width', 512))
        height = round(metadata.get('height', 512))

        if height == width:
            height, width = 512, 512
        elif height > width:
            height, width = 512, -1
        elif width > height:
            height, width = -1, 512

        resized_video = f"{media}.webm"
        cmd = f"ffmpeg -i {media} -ss 00:00:00 -to 00:00:03 -map 0:v -bufsize 256k" + \
            f" -c:v libvpx-vp9 -vf scale={width}:{height},fps=fps=30 {resized_video}"
        await runcmd(cmd)
        os.remove(media)
        return resized_video

    image = Image.open(media)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(media)
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
