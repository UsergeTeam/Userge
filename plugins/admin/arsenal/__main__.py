""" Ban/Kick all """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import time

from pyrogram.errors import FloodWait

from userge import userge, logging, Message, config

_LOG = logging.getLogger(__name__)


async def banager(
    message: Message, chat_id: int, user_id: int, until_date: int
) -> str:
    try:
        await message.client.ban_chat_member(chat_id=chat_id,
                                             user_id=user_id,
                                             until_date=until_date)
        log_msg = 'Success'
    except FloodWait as fw:
        _LOG.info("Sleeping for some time due to flood wait")
        await asyncio.sleep(fw.x + 10)
        return await banager(message, chat_id, user_id, until_date)
    except Exception as u_e:
        if hasattr(u_e, 'NAME'):
            log_msg = (
                f"ERROR:- {u_e.NAME} >>"
                f" {type(u_e).__name__} > {u_e.MESSAGE}"
            )
        else:
            log_msg = f'ERROR:- {type(u_e).__name__} > {str(u_e)}'

    return log_msg


@userge.on_cmd("snap", about={
    'header': "Ban All",
    'description': "Haha, a Mighty Thanos snap to Ban"
    " All Members of a SuperGroup",
    'flags': {'-k': "Kick Members instead of banning"},
    'usage': "{tr}snap [(optional flag)]"},
    allow_private=False, only_admins=True)
async def snapper(message: Message):
    if not message.from_user:
        return
    if (await message.chat.get_member(message.from_user.id)).status != "creator":
        await message.err("required chat creator !")
        return
    chat_id = message.chat.id
    act = 'Banning'
    if '-k' in message.flags:
        act = 'Kicking'
    await message.edit(
        f"⚠️ {act} all Members of the chat. [`Check application logs"
        f" for status`]\nUse `{config.CMD_TRIGGER}cancel` as reply to "
        "this message to stop this process."
    )
    _LOG.info(f'Wiping out Members in {message.chat.title}')
    s_c = 0
    e_c = 0
    async for member in message.client.iter_chat_members(chat_id):
        if message.process_is_canceled:
            await message.edit("`Exiting snap...`")
            break
        if (
            member.status in ("administrator", "creator") or
            member.user.is_self or
            member.user.id in config.OWNER_ID
        ):
            continue
        until = int(time.time()) + 45 if '-k' in message.flags else 0
        log_msg = await banager(message, chat_id, member.user.id, until)
        user_tag = f"[{member.user.first_name}]: Ban Status --> "
        if log_msg.lower() == 'success':
            s_c += 1
        else:
            e_c += 1
        _LOG.info(user_tag + log_msg)
    await message.edit(
        f"[<b>{act} Completed</b>]:\nSuccess: `{s_c}`\nFailed: `{e_c}`"
    )
