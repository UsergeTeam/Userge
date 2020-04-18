# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio

from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError

from userge import userge, Message, Config

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

UPSTREAM_REMOTE = 'upstream'


@userge.on_cmd("update", about="""\
__Check Updates or Update Userge__

**Usage:**

    `.update` : check updates from default branch
    `.update -dev` : check updates from dev branch
    `.update -run` : run updater from default branch
    `.update -run -dev` : run updater from dev branch""", del_pre=True)
async def check_update(message: Message):
    """check or do updates"""

    await message.edit("`Checking for updates, please wait....`")

    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo = Repo.init()

    if UPSTREAM_REMOTE in repo.remotes:
        ups_rem = repo.remote(UPSTREAM_REMOTE)

    else:
        ups_rem = repo.create_remote(UPSTREAM_REMOTE, Config.UPSTREAM_REPO)

    ups_rem.fetch()

    for ref in ups_rem.refs:
        branch = str(ref).split('/')[-1]

        if branch not in repo.branches:
            repo.create_head(branch, ref)

    flags = list(message.flags)

    if "run" in flags:
        run_updater = True
        flags.remove("run")

    else:
        run_updater = False

    if len(flags) == 1:
        branch = flags[0]

    else:
        branch = repo.active_branch.name

    if branch not in repo.branches:
        await message.err(f'invalid branch name : {branch}')
        return

    out = ''
    try:
        for i in repo.iter_commits(f'HEAD..{UPSTREAM_REMOTE}/{branch}'):
            out += f"🔨 **#{i.count()}** : [{i.summary}]({Config.UPSTREAM_REPO.rstrip('/')}/commit/{i}) " + \
                    f"👷 __{i.committer}__\n\n"

    except GitCommandError as error:
        await message.err(error, del_in=5)
        return

    if not out:
        await message.edit(f'**Userge is up-to-date with [{branch}]**', del_in=5)
        return

    if not run_updater:
        changelog_str = f'**New UPDATE available for [{branch}]:\n\n📄 CHANGELOG 📄**\n\n'
        await message.edit_or_send_as_file(changelog_str + out, disable_web_page_preview=True)

    else:
        await message.edit(f'`New update found for [{branch}], trying to update...`')
        repo.git.reset('--hard', 'FETCH_HEAD')

        await CHANNEL.log(f"**UPDATING Userge from [{branch}]:\n\n📄 CHANGELOG 📄**\n\n{out}")

        if Config.HEROKU_GIT_URL:
            await message.edit(
                '`Heroku app found, pushing update...\nthis will take upto 1 min`', del_in=3)

            if "heroku" in repo.remotes:
                remote = repo.remote("heroku")
                remote.set_url(Config.HEROKU_GIT_URL)

            else:
                remote = repo.create_remote("heroku", Config.HEROKU_GIT_URL)

            remote.push(refspec=f'{branch}:master', force=True)

        else:
            await message.edit(
                '**Userge Successfully Updated!**\n'
                '__Now restarting... Wait for a while!__`', del_in=3)

            asyncio.get_event_loop().create_task(userge.restart())
