# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message


@userge.on_cmd("cancel", about={
    'header': "Reply this to message you want to cancel",
    'flags': {'-a': "cancel all tasks"}})
async def cancel_(message: Message):
    if '-a' in message.flags:
        ret = Message._call_all_cancel_callbacks()  # pylint: disable=protected-access
        if ret == 0:
            await message.err("nothing found to cancel", show_help=False)
        return
    replied = message.reply_to_message  # type: Message
    if replied:
        if not replied._call_cancel_callbacks():  # pylint: disable=protected-access
            await message.err("nothing found to cancel", show_help=False)
    else:
        await message.err("source not provided !", show_help=False)
