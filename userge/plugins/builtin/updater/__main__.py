# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from typing import Tuple

from userge import userge, Message
from loader.userge import api

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("update", about={
    'header': "Check Updates or Update Userge",
    'flags': {
        '-pull': "pull updates",
        '-master': "select master branch",
        '-beta': "select beta branch"},
    'usage': "{tr}update : check updates from master branch\n"
             "{tr}update -[branch_name] : check updates from any branch\n"
             "add -pull if you want to pull updates",
    'examples': "{tr}update -beta -pull"}, del_pre=True, allow_channels=False)
async def check_update(message: Message):
    """ check or do updates """
    await message.edit("`Checking for updates, please wait....`")
    flags = list(message.flags)
    pull_from_repo = False
    core = await api.get_core()
    branch = core.branch
    if "pull" in flags:
        pull_from_repo = True
        flags.remove("pull")
    if len(flags) == 1:
        branch = flags[0]
        dev_branch = "alpha"
        if branch == dev_branch:
            await message.err('Can\'t update to unstable [alpha] branch. '
                              'Please use other branches instead !')
            return
    another_branch = core.branch != branch
    if branch not in core.branches:
        return await message.err(f'invalid branch name : {branch}')
    if another_branch and not pull_from_repo:
        return await message.err(
            f'you have to change branch from **{core.branch}** to {branch} to see updates.'
        )
    if another_branch and pull_from_repo:
        await message.edit(
            f'`Moving HEAD from [{core.branch}] >>> [{branch}] ...`', parse_mode='md')
        await CHANNEL.log(f"`Moved HEAD from [{core.branch}] >>> [{branch}] !`")
        await api.set_core_branch(branch)
        await message.edit('`Now restarting... Wait for a while!`', del_in=3)
        await userge.restart(True)
        return

    out, version = await _get_updates()
    if pull_from_repo:
        if out:
            await message.edit(f'`New update found for [{branch}], Now pulling...`')
            await CHANNEL.log(f"**PULLED update from [{branch}]:\n\n📄 CHANGELOG 📄**\n\n{out}")
            await api.set_core_version(version)
            await message.edit('**Userge Successfully Updated!**\n'
                               '`Now restarting... Wait for a while!`', del_in=3)
            await userge.restart(True)
        else:
            await message.err(f'**Userge is up-to-date with [{branch}]**')
    elif out:
        change_log = f'**New UPDATE available for [{branch}]:\n\n📄 CHANGELOG 📄**\n\n'
        await message.edit_or_send_as_file(change_log + out, disable_web_page_preview=True)
    else:
        await message.edit(f'**Userge is up-to-date with [{branch}]**', del_in=5)


async def _get_updates() -> Tuple[str, str]:
    new_commits = await api.get_core_new_commits()
    if new_commits:
        out = ''.join(
            f"🔨 **#{i.count()}** : [{i.summary}]({i.url}) 👷 __{i.author}__\n\n"
            for i in new_commits
        )
        return out, new_commits[-1].version
    return '', ''
