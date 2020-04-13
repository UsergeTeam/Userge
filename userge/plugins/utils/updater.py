# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import asyncio

import heroku3
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
        await CHANNEL.log(f'{ERROR_TEXT}\n`directory {error} is not found`')
        await message.edit(f'{ERROR_TEXT}\n`directory {error} is not found`', del_in=5)
        return

    except InvalidGitRepositoryError as error:
        LOG.warn(
            f'{ERROR_TEXT}\n`directory {error} does not seems to be a git repository`')

        repo = Repo.init()

    except GitCommandError as error:
        await CHANNEL.log(f'{ERROR_TEXT}\n`Early failure! {error}`')
        await message.edit(f'{ERROR_TEXT}\n`Early failure! {error}`', del_in=5)
        return

    try:
        repo.create_remote('upstream', Config.OFFICIAL_REPO_LINK)
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
        await CHANNEL.log(f'{ERROR_TEXT}\n`{error}`')
        await message.edit(f'{ERROR_TEXT}\n`{error}`', del_in=5)
        return

    repo.create_head(branch, getattr(ups_rem.refs, branch))
    getattr(repo.heads, branch).checkout(True)

    out = ''
    for i in repo.iter_commits(f'HEAD..upstream/{branch}'):
        out += f'•[{i.committed_datetime.strftime("%d/%m/%y")}]: {i.summary} <{i.author}>\n'

    if not out:
        await CHANNEL.log(f'**Userge is up-to-date with [{branch}]**')
        await message.edit(f'**Userge is up-to-date with [{branch}]**', del_in=5)
        return

    if not run_updater:
        changelog_str = f'**New UPDATE available for [{branch}]:\n\nCHANGELOG:**\n\n`{out}`'
        await CHANNEL.log(changelog_str)
        await message.edit_or_send_as_file(changelog_str)

    else:
        await message.edit(f'`New update found for [{branch}], trying to update...`')
        repo.git.reset('--hard', 'FETCH_HEAD')

        if Config.HEROKU_API_KEY:
            heroku = heroku3.from_key(Config.HEROKU_API_KEY)
            heroku_app = None

            for heroku_app in heroku.apps():
                if heroku_app and Config.HEROKU_APP_NAME and \
                    heroku_app.name == Config.HEROKU_APP_NAME:
                    break

            if heroku_app:
                await message.edit('`Heroku app found, trying to push update...`')

                heroku_git_url = heroku_app.git_url.replace(
                    "https://",
                    "https://api:" + Config.HEROKU_API_KEY + "@")

                if "heroku" in repo.remotes:
                    remote = repo.remote("heroku")
                    remote.set_url(heroku_git_url)

                else:
                    remote = repo.create_remote("heroku", heroku_git_url)

                remote.push(refspec=f"HEAD:refs/heads/{branch}")

            else:
                await CHANNEL.log("please check your heroku app name")
                await message.reply(
                    "no heroku application found for given name, but a key is given? 😕", del_in=3)

        await CHANNEL.log(f"**UPDATED Userge from [{branch}]:\n\nCHANGELOG:**\n\n`{out}`")

        await message.edit(
            '**Userge Successfully Updated!**\n __Now restarting... Wait for a while!__`', del_in=3)

        asyncio.create_task(restart(userge))


async def restart(client: userge):
    """restart the client"""

    await client.restart()

    LOG.info("USERGE - Restarted")
    await CHANNEL.log("Userge Restarted!")
