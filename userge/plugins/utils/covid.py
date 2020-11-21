# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >

# Userge Plugin for getting detailed stats of Covid Patients
# Author: Sumanjay (https://github.com/cyberboysumanjay) (@cyberboysumanjay)
# All rights reserved.

from covid import Covid

from userge import userge, Message, pool


@userge.on_cmd("covid", about={
    'header': "see covid details",
    'description': "The current real time situation of the COVID-19 patients reported in worldwide",
    'flags': {'-l': "list countries"},
    'usage': "{tr}covid [flag | country]",
    'examples': ["{tr}covid -l", "{tr}covid", "{tr}covid india"]})
async def covid(message: Message):
    await message.edit("`fetching covid ...`")
    covid_ = await pool.run_in_thread(Covid)("worldometers")
    country = message.input_str
    result = ""
    if '-l' in message.flags:
        result += "<u>Covid Supported Countries</u>\n\n`"
        result += '` , `'.join(sorted(filter(lambda x: x, covid_.list_countries())))
        result += "`"
    elif country:
        try:
            data = covid_.get_status_by_country_name(country)
        except ValueError:
            await message.err(f"invalid country name <{country}>!")
            return
        result += f"<u>Covid Status for {data['country']}</u>\n\n"
        result += f"**new cases** : `{data['new_cases']}`\n"
        result += f"**new deaths** : `{data['new_deaths']}`\n\n"
        result += f"**critical** : `{data['critical']}`\n"
        result += f"**active** : `{data['active']}`\n"
        result += f"**confirmed** : `{data['confirmed']}`\n"
        result += f"**deaths** : `{data['deaths']}`\n"
        result += f"**recovered** : `{data['recovered']}`\n\n"
        result += f"**total tests** : `{data['total_tests']}`\n"
        result += f"**total tests per million** : `{data['total_tests_per_million']}`\n"
        result += f"**total cases per million** : `{data['total_cases_per_million']}`\n"
        result += f"**total deaths per million** : `{data['total_deaths_per_million']}`\n"
        result += f"**population** : `{data['population']}`\n"
    else:
        result += "<u>Covid Status in the world</u>\n\n"
        result += f"**total active cases** : `{covid_.get_total_active_cases()}`\n"
        result += f"**total confirmed cases** : `{covid_.get_total_confirmed_cases()}`\n"
        result += f"**total deaths** : `{covid_.get_total_deaths()}`\n"
        result += f"**total recovered** : `{covid_.get_total_recovered()}`\n"
    await message.edit_or_send_as_file(result)
