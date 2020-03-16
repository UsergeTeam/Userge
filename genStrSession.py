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
    asyncio.run(genStrSession())
