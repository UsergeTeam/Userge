# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >

# Userge Plugin for getting detailed stats of Covid Patients
# Author: Sumanjay (https://github.com/cyberboysumanjay) (@cyberboysumanjay)
# All rights reserved.

import aiohttp
from userge import userge, Message


@userge.on_cmd("covid", about={
    'header': "see covid details",
    'description': "The current real time situation of the COVID-19 patients reported in worldwide",
    'usage': "{tr}covid for global\n{tr}covid [country]",
    'countries': "Sri Lanka, USA, Spain, Italy, France, Germany, UK, Turkey, Iran', China, "
                 "Russia, Brazil, Belgium, Canada, Netherlands, Switzerland, India, "
                 "Portugal, Ecuador, Peru, Ireland, Sweden, Saudi Arabia, Austria, "
                 "Israel, Japan, Chile, Singapore, Mexico, Pakistan, "
                 "Poland, S. Korea, Romania, UAE......"})
async def covid(message: Message):
    def fill(nw_c, nw_d, ac_c, cr_c, t_c, t_d, t_r, name, rank):
        output_l = f'''
        <strong><u>COVID-19 ☠ Patients Reported in {name}</u></strong>

        😕 **New Cases** : `{nw_c}`
        😭 **New Deaths** : `{nw_d}`

        😔 **Active Cases** : `{ac_c}`
        😥 **Critical Cases** : `{cr_c}`

        😔 **Total Cases** : `{t_c}`
        😭 **Total Deaths** : `{t_d}`
        😍 **Total Recovered** : `{t_r}`

        😇 **Recovery Rate** : `{round((t_r/t_c)*100,2)}`
        '''
        if rank is not None:
            output_l = output_l + f"🛑 **Danger Rank** : `{rank}`"
        return output_l

    input_ = message.input_str.strip().title()

    if len(input_) == 0:
        try:
            async with aiohttp.ClientSession() as ses:
                async with ses.get("https://sjprojectsapi.herokuapp.com/covid/") as res:
                    data = await res.json()
            global_data = data['results'][0]
            nw_c = global_data['total_new_cases_today']
            nw_d = global_data['total_new_deaths_today']
            ac_c = global_data['total_active_cases']
            cr_c = global_data['total_serious_cases']
            t_c = global_data['total_cases']
            t_d = global_data['total_deaths']
            t_r = global_data['total_recovered']

            output = fill(nw_c, nw_d, ac_c, cr_c, t_c, t_d, t_r, "the world", None)
            await message.edit(output, disable_web_page_preview=True)
        except Exception:
            await message.edit("Covid API is currently down!\nPlease Try Again Later")
    else:
        try:
            async with aiohttp.ClientSession() as ses:
                async with ses.get(
                        "https://sjprojectsapi.herokuapp.com/covid/?country=" + input_) as res:
                    data = await res.json()
            country_data = data['countrydata'][0]
            nw_c = country_data['total_new_cases_today']
            nw_d = country_data['total_new_deaths_today']
            ac_c = country_data['total_active_cases']
            cr_c = country_data['total_serious_cases']
            t_c = country_data['total_cases']
            t_d = country_data['total_deaths']
            t_r = country_data['total_recovered']
            rank = country_data['total_danger_rank']

            output = fill(nw_c, nw_d, ac_c, cr_c, t_c, t_d, t_r, input_, rank)
            await message.edit(output, disable_web_page_preview=True)
        except Exception:
            await message.edit(
                "Either the country name is not correct or country is not in our database!")
