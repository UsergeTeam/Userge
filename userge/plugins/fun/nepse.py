import requests, json
from userge import userge, Message


@userge.on_cmd(
    "nepse",
    about={
        "header": "Nepal Stock details",
        "usage": "/nepse stockSymbol",
        "examples": "/nepse PLI",
    },
)
async def response(message: Message):
    symbol = message.input_str
    csymbol = symbol.upper()
    resp = (
        (
            requests.get(
                f"https://vhl57xdr73.execute-api.us-east-1.amazonaws.com/Beta/Nepse?symbol={csymbol}"
            )
        ).json()
    )["body"]
    await message.edit(resp)
