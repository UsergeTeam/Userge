# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pyrogram import Client
import asyncio


async def genStrSession():
    async with Client(
        "Userge",
        api_id=int(input("enter Telegram APP ID: ")),
        api_hash=input("enter Telegram API HASH: ")
    ) as Userge:
        print(Userge.export_session_string())


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(genStrSession())
