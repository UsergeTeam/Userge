# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import json
from datetime import datetime

import aiohttp
from pytz import country_timezones as c_tz, timezone as tz, country_names as c_n

from userge import userge, Message, Config

CHANNEL = userge.getCLogger(__name__)


async def get_tz(con):
    """Get time zone of the given country
    Credits: @aragon12 and @zakaryan2004
    """
    for c_code in c_n:
        if con == c_n[c_code]:
            return tz(c_tz[c_code][0])
    try:
        if c_n[con]:
            return tz(c_tz[con][0])
    except KeyError:
        return


@userge.on_cmd("weather", about={
    'header': "use this to get weather details",
    'description': "get weather info for any city",
    'examples': [
        "{tr}weather (default city)",
        "{tr}weather colombo (city name)"]})
async def weather_get(message: Message):
    """
    this function can get weather info
    """
    OWM_API = Config.OPEN_WEATHER_MAP
    if not OWM_API:
        await message.edit(
            "<code>Oops!!get the API from</code> "
            "<a href='https://openweathermap.org'>HERE</a> "
            "<code>& add it to Heroku config vars</code> (<code>OPEN_WEATHER_MAP</code>)",
            disable_web_page_preview=True,
            parse_mode="html", del_in=0)
        return

    APPID = OWM_API

    if not message.input_str:
        CITY = Config.WEATHER_DEFCITY
        if not CITY:
            await message.edit("`Please specify a city or set one as default!`", del_in=0)
            return
    else:
        CITY = message.input_str

    timezone_countries = {
        timezone: country
        for country, timezones in c_tz.items() for timezone in timezones
    }

    if "," in CITY:
        newcity = CITY.split(",")
        if len(newcity[1]) == 2:
            CITY = newcity[0].strip() + "," + newcity[1].strip()
        else:
            country = await get_tz((newcity[1].strip()).title())
            try:
                countrycode = timezone_countries[f'{country}']
            except KeyError:
                await message.edit("`Invalid country.`", del_in=0)
                return
            CITY = newcity[0].strip() + "," + countrycode.strip()

    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={APPID}'
    async with aiohttp.ClientSession() as ses:
        async with ses.get(url) as res:
            req_status = res.status
            res_text = await res.text()
    result = json.loads(res_text)

    if req_status != 200:
        await message.edit(r"`Invalid country.. ¯\_(ツ)_/¯`", del_in=0)
        return

    cityname = result['name']
    curtemp = result['main']['temp']
    humidity = result['main']['humidity']
    min_temp = result['main']['temp_min']
    max_temp = result['main']['temp_max']
    desc = result['weather'][0]
    desc = desc['main']
    country = result['sys']['country']
    sunrise = result['sys']['sunrise']
    sunset = result['sys']['sunset']
    wind = result['wind']['speed']
    winddir = result['wind']['deg']

    ctimezone = tz(c_tz[country][0])
    time = datetime.now(ctimezone).strftime("%A, %I:%M %p")
    fullc_n = c_n[f"{country}"]
    # dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    #        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

    div = (360 / len(dirs))
    funmath = int((winddir + (div / 2)) / div)
    findir = dirs[funmath % len(dirs)]
    kmph = str(wind * 3.6).split(".")
    mph = str(wind * 2.237).split(".")

    def fahrenheit(f):
        temp = str(((f - 273.15) * 9 / 5 + 32)).split(".")
        return temp[0]

    def celsius(c):
        temp = str((c - 273.15)).split(".")
        return temp[0]

    def sun(unix):
        xx = datetime.fromtimestamp(unix, tz=ctimezone).strftime("%I:%M %p")
        return xx

    await message.edit(
        f"**Temperature:** `{celsius(curtemp)}°C | {fahrenheit(curtemp)}°F`\n"
        +
        f"**Min. Temp.:** `{celsius(min_temp)}°C | {fahrenheit(min_temp)}°F`\n"
        +
        f"**Max. Temp.:** `{celsius(max_temp)}°C | {fahrenheit(max_temp)}°F`\n"
        + f"**Humidity:** `{humidity}%`\n" +
        f"**Wind:** `{kmph[0]} kmh | {mph[0]} mph, {findir}`\n" +
        f"**Sunrise:** `{sun(sunrise)}`\n" +
        f"**Sunset:** `{sun(sunset)}`\n\n\n" + f"**{desc}**\n" +
        f"`{cityname}, {fullc_n}`\n" + f"`{time}`")
    await CHANNEL.log(f"check `{CITY}` weather results")
