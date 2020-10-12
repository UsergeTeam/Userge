import re, asyncio
from asyncio import sleep
from re import sub
from userge import userge, Message

            

@userge.on_cmd("Thanos$", about={'header': "just for fun"})
               trigger='', allow_via_bot=False)
async def Thanos_(message: Message):

    """Thanos"""

    animation_interval = 0.8

    animation_ttl = range(70)

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

