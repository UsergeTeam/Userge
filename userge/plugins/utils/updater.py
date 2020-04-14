# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userge import userge, Message, Config

LOG = userge.getLogger(__name__)
CHANNEL = userge.getCLogger(__name__)

ERROR_TEXT = "`Oops.. Updater cannot continue due to some problems occured`\n\n**LOGTRACE:**\n"


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

    except NoSuchPathError as error:
        await message.edit(
            f'{ERROR_TEXT}\n`directory {error} is not found`', del_in=5, log=True)
        return

    except GitCommandError as error:
        await message.edit(
            f'{ERROR_TEXT}\n`Early failure! {error}`', del_in=5, log=True)
        return

    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote('upstream', Config.UPSTREAM_REPO)
        origin.fetch()
        repo.create_head('master', origin.refs.master)
        repo.heads.master.checkout(True)

    try:
        repo.create_remote('upstream', Config.UPSTREAM_REPO)
    except GitCommandError:
        pass

    ups_rem = repo.remote('upstream')
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

    try:
        ups_rem.fetch(branch)
    except GitCommandError as error:
        await message.edit(f'{ERROR_TEXT}\n`{error}`', del_in=5, log=True)
        return

    out = ''
    for i in repo.iter_commits(f'HEAD..upstream/{branch}'):
        out += f"🔨 **#{i.count()}** : [{i.summary}]({Config.UPSTREAM_REPO.rstrip('/')}/commit/{i}) " + \
                f"👷 __{i.committer}__\n\n"

    if not out:
        await message.edit(
            f'**Userge is up-to-date with [{branch}]**', del_in=5, log=True)
        return

    if not run_updater:
        changelog_str = f'**New UPDATE available for [{branch}]:\n\n📄 CHANGELOG 📄**\n\n'
        await message.edit_or_send_as_file(
            changelog_str + out, log=True, disable_web_page_preview=True)

    else:
        await message.edit(f'`New update found for [{branch}], trying to update...`')
        repo.git.reset('--hard', 'FETCH_HEAD')

        if Config.HEROKU_GIT_URL:
            await message.edit('`Heroku app found, trying to push update...`')

            if "heroku" in repo.remotes:
                remote = repo.remote("heroku")
                remote.set_url(Config.HEROKU_GIT_URL)

            else:
                remote = repo.create_remote("heroku", Config.HEROKU_GIT_URL)

            remote.push(refspec=f"HEAD:refs/heads/{branch}")

        await CHANNEL.log(f"**UPDATED Userge from [{branch}]:\n\n📄 CHANGELOG 📄**\n\n{out}")

        await message.edit(
            '**Userge Successfully Updated!**\n __Now restarting... Wait for a while!__`', del_in=3)

        asyncio.get_event_loop().create_task(restart(userge))


async def restart(client: userge):
    """restart the client"""

    await client.restart()

    LOG.info("USERGE - Restarted")
    await CHANNEL.log("Userge Restarted!")
