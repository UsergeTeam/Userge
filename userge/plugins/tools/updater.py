# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
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
        '-push': "push updates to heroku",
        '-master': "select master branch",
        '-beta': "select beta branch",
        '-alpha': "select alpha branch"},
    'usage': "{tr}update : check updates from default branch\n"
             "{tr}update -[branch_name] : check updates from any branch\n"
             "add -pull if you want to pull updates\n"
             "add -push if you want to push updates to heroku",
    'examples': "{tr}update -beta -pull -push"}, del_pre=True, allow_channels=False)
async def check_update(message: Message):
    """ check or do updates """
    await message.edit("`Checking for updates, please wait....`")
    repo = Repo()
    ups_rem = repo.remote(Config.UPSTREAM_REMOTE)
    try:
        ups_rem.fetch()
    except GitCommandError as error:
        await message.err(error, del_in=5)
        return
    for ref in ups_rem.refs:
        branch = str(ref).split('/')[-1]
        if branch not in repo.branches:
            repo.create_head(branch, ref)
    flags = list(message.flags)
    pull_from_repo = False
    push_to_heroku = False
    branch = "master"
    if "pull" in flags:
        pull_from_repo = True
        flags.remove("pull")
    if "push" in flags:
        push_to_heroku = True
        flags.remove("push")
    if len(flags) == 1:
        branch = flags[0]
    if branch not in repo.branches:
        await message.err(f'invalid branch name : {branch}')
        return
    out = ''
    try:
        for i in repo.iter_commits(f'HEAD..{Config.UPSTREAM_REMOTE}/{branch}'):
            out += (f"🔨 **#{i.count()}** : "
                    f"[{i.summary}]({Config.UPSTREAM_REPO.rstrip('/')}/commit/{i}) "
                    f"👷 __{i.committer}__\n\n")
    except GitCommandError as error:
        await message.err(error, del_in=5)
        return
    if out:
        if pull_from_repo:
            await message.edit(f'`New update found for [{branch}], Now pulling...`')
            await asyncio.sleep(1)
            repo.git.reset('--hard', 'FETCH_HEAD')
            await CHANNEL.log(f"**UPDATED Userge from [{branch}]:\n\n📄 CHANGELOG 📄**\n\n{out}")
        elif not push_to_heroku:
            changelog_str = f'**New UPDATE available for [{branch}]:\n\n📄 CHANGELOG 📄**\n\n'
            await message.edit_or_send_as_file(changelog_str + out, disable_web_page_preview=True)
            return
    elif not push_to_heroku:
        await message.edit(f'**Userge is up-to-date with [{branch}]**', del_in=5)
        return
    if not push_to_heroku:
        await message.edit(
            '**Userge Successfully Updated!**\n'
            '`Now restarting... Wait for a while!`', del_in=3)
        asyncio.get_event_loop().create_task(userge.restart(update_req=True))
        return
    if not Config.HEROKU_GIT_URL:
        await message.err("please set heroku things...")
        return
    await message.edit(
        f'`Now pushing updates from [{branch}] to heroku...\n'
        'this will take upto 3 min`\n\n'
        f'* **Restart** me after about 3 min using `{Config.CMD_TRIGGER}restart -h`\n\n'
        '* After restarted successfully, check updates again :)')
    if "heroku" in repo.remotes:
        remote = repo.remote("heroku")
        remote.set_url(Config.HEROKU_GIT_URL)
    else:
        remote = repo.create_remote("heroku", Config.HEROKU_GIT_URL)
    remote.push(refspec=f'{branch}:master', force=True)
    await message.edit(f"**HEROKU APP : {Config.HEROKU_APP.name} is up-to-date with [{branch}]**")
