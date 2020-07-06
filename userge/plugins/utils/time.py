# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from datetime import datetime as dt
from pytz import timezone
from userge import userge, Message, Config

LOG = userge.getLogger(__name__)  # logger object


@userge.on_cmd("dt", about={
    'header': "Get the time and date of a City/Country/Timezone.",
    'flags': {
        '-l': "Gives list of all Country/City Combos for Heroku Config"},
    'usage': "Use {tr}dt to show the Time & Date of your predefined City\n"
             "Use {tr}dt -l to display all TZ Combo's for the Config\n",
    'examples': ['{tr}dt', '{tr}dt [Flag]']},
    del_pre=True)
async def grabTime(message: Message):
    LOG.info("Starting Time command...")
    defaultMessage = (
        "<code>Below is a list of all the Timezones Avaliable</code> \n<a "
        "href=https://pastebin.com/raw/0KSh9CMj>Click Here!</a>\n<code>Enter"
        " one in your Heroku Config Under</code> (<code>COUNTRY_CITY</code>)\n"
        "<code>Ex: America/Los_Angeles</code>")

    if 'l' in message.flags:
        LOG.info("Time: List Flag Used: Giving TZ list...")
        await message.edit(defaultMessage, disable_web_page_preview=True,
                           parse_mode="html", del_in=30)
        return

    if not Config.COUNTRY_CITY:
        LOG.info("Time: No Config Set")
        await message.edit(defaultMessage, disable_web_page_preview=True,
                           parse_mode="html", del_in=30)
        return
    else:
        tz = Config.COUNTRY_CITY

    tzDateTime = dt.now(timezone(tz))
    date = tzDateTime.strftime('%d-%m-%Y')
    militaryTime = tzDateTime.strftime('%H:%M')
    time = dt.strptime(militaryTime, "%H:%M").strftime("%I:%M %p")
    await message.edit("It is currently " + time + " on " + date + " in " +
                       tz.replace("_", " "))
    LOG.info("Time: Command Finished Successfully")
