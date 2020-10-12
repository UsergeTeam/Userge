#This plugin is created by Mahi , only for fun purpose, I'm not a coder😜

import re, asyncio
from asyncio import sleep
from re import sub
from userge import userge, Message

            

@userge.on_cmd("thanos$", about={'header': "Thanos Ki pehli beggum😜"})

async def thanos_(message: Message):

    """thanos"""

    animation_interval = 0.4
    animation_ttl = range(0, 10)
    await message.edit("Wo")
    animation_chars = [
            "abhi",    
            "apni",
            "1st begam",
            "se",
            "teeth",
            "lock",
            "karne",
            "jati",    
            "😜",
            "😐",
        ]

    for i in animation_ttl:

            await asyncio.sleep(animation_interval)

            await message.edit(animation_chars[i % 10])

