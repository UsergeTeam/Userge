# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import requests
from userge import userge, Message


@userge.on_cmd("covid", about={
    'header': "see covid details",
    'description': "The current real time situation of the COVID-19 patients reported in worldwide",
    'usage': ".covid for global\n.covid [country]",
    'countries': "Sri Lanka, USA, Spain, Italy, France, Germany, UK, Turkey, Iran', China, "
                 "Russia, Brazil, Belgium, Canada, Netherlands, Switzerland, India, "
                 "Portugal, Ecuador, Peru, Ireland, Sweden, Saudi Arabia, Austria, "
                 "Israel, Japan, Chile, Singapore, Mexico, Pakistan, "
                 "Poland, S. Korea, Romania, UAE......"})
async def covid(message: Message):
    """covid"""

    input_ = message.input_str.title()
    # Country Wise Data Reciever
    r_c = requests.get('https://akashraj.tech/corona/api')
    r_json = r_c.json()
    set_count_country = r_json['countries_stat']
    set_data = r_json['statistic_taken_at'].split(' ')[0]
    set_count_globe = r_json['world_total']

    if not input_:
        await message.edit(f'''
<strong><u>COVID-19 ☠ Patients Reported in Global</u></strong>

    😕 **New Cases** : `{set_count_globe['new_cases']}`
    😭 **New Deaths** : `{set_count_globe['new_deaths']}`

    😔 **Active Cases** : `{set_count_globe['active_cases']}`
    😥 **Critical Cases** : `{set_count_globe['serious_critical']}`

    😔 **Total Cases** : `{set_count_globe['total_cases']}`
    😭 **Total Deaths** : `{set_count_globe['total_deaths']}`
    😍 **Total Recovered** : `{set_count_globe['total_recovered']}`

**Last Update** : __{set_data}__
**References** : <a href="https://www.worldometers.info/coronavirus/">worldometers.info</a>
''', disable_web_page_preview=True)
    else:
        flag = 0
        for i in range(len(set_count_country)):
            if set_count_country[i]['country_name'] == input_ or \
                set_count_country[i]['country_name'] == input_.upper():
                set_country = set_count_country[i]
                flag = 1
                break
        if flag == 1:
            await message.edit(f'''
<strong><u>COVID-19 ☠ Patients Reported in {set_country['country_name']}</u></strong>

    😕 **New Cases** : `{set_country['new_cases']}`
    😭 **New Deaths** : `{set_country['new_deaths']}`

    😔 **Active Cases** : `{set_country['active_cases']}`
    😥 **Critical Cases** : `{set_country['serious_critical']}`

    😔 **Total Cases** : `{set_country['cases']}`
    😭 **Total Deaths** : `{set_country['deaths']}`
    😍 **Total Recovered** : `{set_country['total_recovered']}`

**Last Update** : __{set_data}__
**References** : <a href="https://www.worldometers.info/coronavirus/">worldometers.info</a>
''', disable_web_page_preview=True)
        else:
            await message.edit(
                "invalid country or statistics of this country hasn't in our database☹", del_in=5)
