# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from git import Repo
from git.exc import GitCommandError

from userge import userge, Message, Config

LOG = userge.getLogger(__name__)
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
    branch = "master"
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
    repo = Repo()
    if branch not in repo.branches:
        await message.err(f'invalid branch name : {branch}')
        return
    try:
        out = _get_updates(repo, branch)
    except GitCommandError as g_e:
        await message.err(g_e, del_in=5)
        return
    if pull_from_repo:
        if out:
            await message.edit(f'`New update found for [{branch}], Now pulling...`')
            await _pull_from_repo(repo, branch)
            await CHANNEL.log(f"**PULLED update from [{branch}]:\n\n📄 CHANGELOG 📄**\n\n{out}")
            await message.edit('**Userge Successfully Updated!**\n'
                               '`Now restarting... Wait for a while!`', del_in=3)
            asyncio.get_event_loop().create_task(userge.restart(True))
        else:
            active = repo.active_branch.name
            if active == branch:
                await message.err(f"already in [{branch}]!")
                return
            await message.edit(
                f'`Moving HEAD from [{active}] >>> [{branch}] ...`', parse_mode='md')
            await _pull_from_repo(repo, branch)
            await CHANNEL.log(f"`Moved HEAD from [{active}] >>> [{branch}] !`")
            await message.edit('`Now restarting... Wait for a while!`', del_in=3)
            asyncio.get_event_loop().create_task(userge.restart())
    elif out:
        change_log = f'**New UPDATE available for [{branch}]:\n\n📄 CHANGELOG 📄**\n\n'
        await message.edit_or_send_as_file(change_log + out, disable_web_page_preview=True)
    else:
        await message.edit(f'**Userge is up-to-date with [{branch}]**', del_in=5)


def _get_updates(repo: Repo, branch: str) -> str:
    repo.remote(Config.UPSTREAM_REMOTE).fetch(branch)
    upst = Config.UPSTREAM_REPO.rstrip('/')
    return ''.join(
        f"🔨 **#{i.count()}** : [{i.summary}]({upst}/commit/{i}) 👷 __{i.author}__\n\n"
        for i in repo.iter_commits(f'HEAD..{Config.UPSTREAM_REMOTE}/{branch}')
    )


async def _pull_from_repo(repo: Repo, branch: str) -> None:
    repo.git.checkout(branch, force=True)
    repo.git.reset('--hard', branch)
    repo.remote(Config.UPSTREAM_REMOTE).pull(branch, force=True)
    await asyncio.sleep(1)
