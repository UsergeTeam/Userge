# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import json

import aiohttp
from emoji import get_emoji_regexp

from userge import userge, Message, Config

CHANNEL = userge.getCLogger(__name__)
LOG = userge.getLogger(__name__)


@userge.on_cmd("cr", about={
    'header': "use this to convert currency & get exchange rate",
    'description': "Convert currency & get exchange rates.",
    'examples': "{tr}cr 1 BTC USD"})
async def cur_conv(message: Message):
    """
    this function can get exchange rate results
    """
    if Config.CURRENCY_API is None:
        await message.edit(
            "<code>Oops!!get the API from</code> "
            "<a href='https://free.currencyconverterapi.com'>HERE</a> "
            "<code>& add it to Heroku config vars</code> (<code>CURRENCY_API</code>)",
            disable_web_page_preview=True,
            parse_mode="html", del_in=0)
        return

    filterinput = get_emoji_regexp().sub(u'', message.input_str)
    curcon = filterinput.upper().split()

    if len(curcon) == 3:
        amount, currency_to, currency_from = curcon
    else:
        await message.err("you entered invalid data")
        return

    if amount.isdigit():
        url = ("https://free.currconv.com/api/v7/convert?"
               f"apiKey={Config.CURRENCY_API}&q="
               f"{currency_from}_{currency_to}&compact=ultra")
        async with aiohttp.ClientSession() as ses, ses.get(url) as res:
            data = json.loads(await res.text())
        try:
            result = data[f'{currency_from}_{currency_to}']
        except KeyError:
            LOG.info(data)
            await message.edit("`invalid response from api !`", del_in=5)
            return
        result = float(amount) / float(result)
        result = round(result, 5)
        await message.edit(
            "**CURRENCY EXCHANGE RATE RESULT:**\n\n"
            f"`{amount}` **{currency_to}** = `{result}` **{currency_from}**")
        await CHANNEL.log("`cr` command executed sucessfully")

    else:
        await message.edit(
            r"`This seems to be some alien currency, which I can't convert right now.. (⊙_⊙;)`",
            del_in=0)
