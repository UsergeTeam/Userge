""" create text using weeby font """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from userge import userge, Message

normal_char = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
    'v', 'w', 'x', 'y', 'z'
]

weeby_char = [
    '卂', '乃', '匚', '刀', '乇', '下', '厶', '卄', '工', '丁',
    '长', '乚', '从', '𠘨', '口', '尸', '㔿', '尺', '丂', '丅', '凵',
    'リ', '山', '乂', '丫', '乙'
]


@userge.on_cmd("weebify", about={
    'header': "Weebify",
    'description': "create text in a weeb style",
    'usage': "{tr}weebify [text | reply]"})
async def _weeb_text(message: Message):
    args = message.input_or_reply_str
    if not args:
        await message.edit(
            "try:\n    weebify\nexcept **Exception** as **Intelligence**:"
            f"\n    print({message.from_user.first_name})"
        )
        return
    str_ = ' '.join(args).lower()
    for nor_c in str_:
        if nor_c in normal_char:
            weeb_c = weeby_char[normal_char.index(nor_c)]
            str_ = str_.replace(nor_c, weeb_c)
    await message.edit(str_)
