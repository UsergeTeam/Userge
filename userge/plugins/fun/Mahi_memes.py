import re, asyncio
from asyncio import sleep
from re import sub
from userge import userge, Message

            

@userge.on_cmd("thanos$", about={'header': "just for fun"})

async def thanos_(message: Message):

    """thanos"""

    animation_interval = 0.8
    animation_ttl = range(11)
    await message.edit("Thanos")
    animation_chars = [
            "wo",
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

            await message.edit(animation_chars[i % 11])

