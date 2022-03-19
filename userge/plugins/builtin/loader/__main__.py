# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from typing import List

from loader.types import Update
from loader.userge import api
from userge import userge, Message, config
from userge.versions import get_version

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("core", about={
    'header': "view or manage the core repository",
    'flags': {
        '-f': "fetch core repo",
        '-n': "view available new commits",
        '-o': "view old commits (default limit 20)",
        '-b': "change branch",
        '-v': "change version"},
    'usage': "{tr}core [flags]",
    'examples': [
        "{tr}core : see core repo info",
        "{tr}core -f", "{tr}core -n",
        "{tr}core -f -n : fetch and get updates",
        "{tr}core -o", "{tr}core -o=20 : limit results to 20",
        "{tr}core -b=master",
        "{tr}core -v=750 : update id (grab using {tr}core -n or {tr}core -o)"]
}, del_pre=True, allow_channels=False)
async def core(message: Message):
    """ view or manage the core repository """
    flags = message.flags

    fetch = 'f' in flags
    get_new = 'n' in flags
    get_old, old_limit = 'o' in flags, int(flags.get('o') or 20)
    set_branch, branch = 'b' in flags, flags.get('b')
    set_version, version = 'v' in flags, int(flags.get('v') or 0)

    await message.edit("```processing ...```")

    if fetch:
        await api.fetch_core()

    if get_new:
        updates = await api.get_core_new_commits()

        if not updates:
            await message.edit("no new commits available for core repo", del_in=3)
            return

        out = _updates_to_str(updates)
        await message.edit_or_send_as_file(
            f"**{len(updates)}** new commits available for core repo\n\n{out}",
            del_in=0, disable_web_page_preview=True)

    elif get_old:
        updates = await api.get_core_old_commits(old_limit)

        if not updates:
            await message.edit("no old commits available for core repo", del_in=3)
            return

        out = _updates_to_str(updates)
        await message.edit_or_send_as_file(
            f"**{len(updates)}** old commits of core repo\n\n{out}",
            del_in=0, disable_web_page_preview=True)

    elif set_branch or set_version:
        if not branch and not version:
            await message.err("invalid flags")
            return

        core_repo = await api.get_core()

        if version:
            if version == core_repo.count:
                await message.edit(f"already on this version: `{version}`", del_in=3)
                return

            if version > core_repo.max_count:
                await message.err(
                    f"invalid version: {version} max: {core_repo.max_count}", show_help=False)
                return

        if branch and branch not in core_repo.branches:
            await message.err(f"invalid branch: {branch}", show_help=False)
            return

        if await api.edit_core(branch, version or None):
            await message.edit(
                f"done, do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)
        else:
            await message.edit("```didn't change anything```", del_in=3)

    elif fetch:
        await message.edit("```fetched core repo```", del_in=3)

    else:
        core_repo = await api.get_core()

        out = f"""**Core Details**

**name** : [{core_repo.name}]({core_repo.url})
**version** : `{get_version()}`
**version code** : `{core_repo.count}`
**branch** : `{core_repo.branch}`
**branches** : `{'`, `'.join(core_repo.branches)}`
**is latest** : `{core_repo.count == core_repo.max_count}`
**head** : [link]({core_repo.head_url})"""

        await message.edit(out, del_in=0, disable_web_page_preview=True)


@userge.on_cmd("repos", about={
    'header': "view or manage plugins repositories",
    'flags': {
        '-f': "fetch one or all plugins repos",
        '-id': "plugins repo id (grab using {tr}repos)",
        '-n': "view available new commits",
        '-o': "view old commits (default limit 20)",
        '-b': "change branch",
        '-v': "change version",
        '-p': "change priority (-p2 > -p1)",
        '-invalidate': "notify loader to rebuild all the plugins"},
    'usage': "{tr}repos [flags]",
    'examples': [
        "{tr}repos : see plugins repos info",
        "{tr}repos -f : fetch all plugins repos",
        "{tr}repos -id=1 -f : only fetch this repo",
        "{tr}repos -id=1 -n",
        "{tr}repos -f -id=1 -n : fetch and get updates",
        "{tr}repos -id=1 -o", "{tr}repos -id=1 -o=20 : limit results to 20",
        "{tr}repos -id=1 -b=master",
        "{tr}repos -id=1 -v=750 : update id (grab using -n or -o flags)",
        "{tr}repos -id=1 -p=5", "{tr}repos -invalidate"]}, del_pre=True, allow_channels=False)
async def repos(message: Message):
    """ view or manage plugins repositories """
    flags = message.flags

    fetch, invalidate = 'f' in flags, 'invalidate' in flags
    repo_id = int(flags.get('id') or 0)
    get_new = 'n' in flags
    get_old, old_limit = 'o' in flags, int(flags.get('o') or 20)
    set_branch, branch = 'b' in flags, flags.get('b')
    set_version, version = 'v' in flags, int(flags.get('v') or 0)
    set_priority, priority = 'p' in flags, flags.get('p')

    await message.edit("```processing ...```")

    if repo_id <= 0:
        if fetch:
            await api.fetch_repos()
            await message.edit("```fetched plugins repos```", del_in=3)

        elif invalidate:
            await api.invalidate_repos_cache()
            await message.edit(
                "plugins cache invalidated, "
                f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

        else:
            plg_repos = await api.get_repos()

            if not plg_repos:
                await message.edit("```no repos found```", del_in=3)
                return

            out = "**Repos Details**\n\n"

            for plg_repo in plg_repos:
                out += f"**name** : [{plg_repo.name}]({plg_repo.url})\n"
                out += f"**id** : `{plg_repo.id}`\n"
                out += f"**priority** : `{plg_repo.priority}`\n"
                out += f"**version code** : `{plg_repo.count}`\n"
                out += f"**branch** : `{plg_repo.branch}`\n"
                out += f"**branches** : `{'`, `'.join(plg_repo.branches)}`\n"
                out += f"**is latest** : `{plg_repo.count == plg_repo.max_count}`\n"
                out += f"**head** : [link]({plg_repo.head_url})\n\n"

            await message.edit_or_send_as_file(out, del_in=0, disable_web_page_preview=True)

    else:
        if fetch:
            await api.fetch_repo(repo_id)

        repo_details = await api.get_repo(repo_id)

        if not repo_details:
            await message.err(f"invalid repo_id: {repo_id}")
            return

        if get_new:
            updates = await api.get_repo_new_commits(repo_id)

            if not updates:
                await message.edit(f"no new commits available for repo: {repo_id}", del_in=3)
                return

            out = _updates_to_str(updates)
            await message.edit_or_send_as_file(
                f"**{len(updates)}** new commits available for repo: `{repo_id}`\n\n{out}",
                del_in=0, disable_web_page_preview=True)

        elif get_old:
            updates = await api.get_repo_old_commits(repo_id, old_limit)

            if not updates:
                await message.edit(f"no old commits available for repo: {repo_id}", del_in=3)
                return

            out = _updates_to_str(updates)
            await message.edit_or_send_as_file(
                f"**{len(updates)}** old commits of repo: `{repo_id}`\n\n{out}",
                del_in=0, disable_web_page_preview=True)

        elif set_branch or set_version or set_priority:
            if not branch and not version and not priority:
                await message.err("invalid flags")
                return

            if version:
                if version == repo_details.count:
                    await message.edit(f"already on this version: `{version}`", del_in=3)
                    return

                if version > repo_details.max_count:
                    await message.err(
                        f"invalid version: {version} max: {repo_details.max_count}",
                        show_help=False)
                    return

            if priority:
                if priority == repo_details.priority:
                    await message.edit(f"already on this priority: `{priority}`", del_in=3)
                    return

                priority = int(priority)

            if branch and branch not in repo_details.branches:
                await message.err(f"invalid branch: {branch}", show_help=False)
                return

            if await api.edit_repo(repo_id, branch, version or None, priority):
                await message.edit(
                    f"done, do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)
            else:
                await message.edit("```didn't change anything```", del_in=3)

        elif fetch:
            await message.edit(f"```fetched plugins repo: {repo_id}```", del_in=3)

        else:
            await message.err("invalid flags")


@userge.on_cmd("addrepo", about={
    'header': "add a plugins repo",
    'flags': {
        '-b': "branch name (optional|default master)",
        '-p': "priority (optional|default 1)"},
    'usage': "{tr}addrepo [flags] url",
    'others': "plugins of higher priority repos will override plugins of low priority repos",
    'examples': [
        "{tr}addrepo https://github.com/UsergeTeam/Userge-Plugins",
        "{tr}addrepo -b=master https://github.com/UsergeTeam/Userge-Plugins",
        "{tr}addrepo -b=master -p=1 https://github.com/UsergeTeam/Userge-Plugins"]
}, del_pre=True, allow_channels=False)
async def add_repo(message: Message):
    """ add a plugins repo """
    flags = message.flags

    branch = flags.get('b', "master")
    priority = int(flags.get('p') or 1)
    url = message.filtered_input_str

    if not url:
        await message.err("no input url")
        return

    await message.edit("```processing ...```")

    if await api.add_repo(priority, branch, url):
        await message.edit("added repo, "
                           f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

    else:
        await message.edit("```repo was already added or invalid```", del_in=3)


@userge.on_cmd("rmrepo", about={
    'header': "remove a plugins repo",
    'flags': {'-id': "plugins repo id (grab using {tr}repos)"},
    'usage': "{tr}rmrepo [flag]",
    'examples': "{tr}rmrepo -id=2"}, del_pre=True, allow_channels=False)
async def rm_repo(message: Message):
    """ remove a plugins repo """
    repo_id = message.flags.get('id')

    if not repo_id or not repo_id.isnumeric():
        await message.err("empty or invalid repo id")
        return

    await message.edit("```processing ...```")

    if await api.remove_repo(int(repo_id)):
        await message.edit("removed repo, "
                           f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

    else:
        await message.edit("```couldn't find that repo```", del_in=3)


@userge.on_cmd("consts", about={
    'header': "view all constraints",
    'usage': "{tr}consts"}, del_pre=True, allow_channels=False)
async def consts(message: Message):
    """ view all constraints """
    data_ = await api.get_constraints()

    if not data_:
        await message.edit("```no constraints found```", del_in=3)
        return

    out = ""

    for const in data_:
        out += f"type: `{const.type}`\ndata: `{'`, `'.join(const.data)}`\n\n"

    await message.edit_or_send_as_file(out, del_in=0)


@userge.on_cmd("addconsts", about={
    'header': "add constraints",
    'description': "can ignore plugins, categories or even them from specific repos easily",
    'flags': {'-type': "constraints type (include|exclude|in)"},
    'usage': "{tr}addconsts [flag] data",
    'data_types': ["plugin", "category/", "repo/plugin", "repo/category/"],
    'examples': [
        "{tr}addconsts -type=exclude executor sudo",
        "{tr}addconsts -type=exclude fun/",
        "{tr}addconsts -type=include usergeteam.userge-plugins/executor",
        "{tr}addconsts -type=exclude usergeteam.userge-plugins/fun/",
        "{tr}addconsts -type=in executor help fun/ usergeteam.userge-plugins/video_call"]
}, del_pre=True, allow_channels=False)
async def add_consts(message: Message):
    """ add constraints """
    c_type = message.flags.get('type', '').lower()

    if c_type not in ('include', 'exclude', 'in'):
        await message.err("empty or invalid type")
        return

    data = message.filtered_input_str

    if not data:
        await message.err("no data provided")
        return

    await message.edit("```processing ...```")

    if await api.add_constraints(c_type, data.split()):
        await message.edit("added constraints, "
                           f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

    else:
        await message.edit("```didn't add anything```", del_in=3)


@userge.on_cmd("rmconsts", about={
    'header': "remove constraints",
    'description': "if the type is provided, "
                   "then the constraints only in this type will be removed",
    'flags': {
        '-type': "constraints type (include|exclude|in) (optional)"},
    'usage': "{tr}rmconsts [flag] data",
    'data_types': ["plugin", "category/", "repo/plugin", "repo/category/"],
    'examples': [
        "{tr}rmconsts -type=exclude executor sudo",
        "{tr}rmconsts fun/",
        "{tr}rmconsts executor help fun/ usergeteam.userge-plugins/video_call"]
}, del_pre=True, allow_channels=False)
async def rm_consts(message: Message):
    """ remove constraints """
    c_type = message.flags.get('type', '').lower() or None

    if c_type and c_type not in ('include', 'exclude', 'in'):
        await message.err("invalid type")
        return

    data = message.filtered_input_str

    if not data:
        await message.err("no data provided")
        return

    await message.edit("```processing ...```")

    if await api.remove_constraints(c_type, data.split()):
        await message.edit("removed constraints, "
                           f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

    else:
        await message.edit("```didn't remove anything```", del_in=3)


@userge.on_cmd("clrconsts", about={
    'header': "clear constraints",
    'description': "if the type is provided, "
                   "then the constraints only in this type will be cleared",
    'flags': {
        '-type': "constraints type (include|exclude|in) (optional)"},
    'usage': "{tr}clrconsts [flag]",
    'examples': [
        "{tr}clrconsts -type=exclude",
        "{tr}clrconsts"]
}, del_pre=True, allow_channels=False)
async def clr_consts(message: Message):
    """ clear constraints """
    c_type = message.flags.get('type', '').lower() or None

    if c_type and c_type not in ('include', 'exclude', 'in'):
        await message.err("invalid type")
        return

    await message.edit("```processing ...```")

    if await api.clear_constraints(c_type):
        await message.edit("cleared constraints, "
                           f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)

    else:
        await message.edit("```nothing found to clear```", del_in=3)


@userge.on_cmd("update", about={
    'header': "Check Updates or Update Userge",
    'description': "use {tr}core and {tr}repos, "
                   "if you want more advanced control over version controlling",
    'flags': {
        '-c': "view updates for core repo",
        '-r': "view updates for all plugins repos",
        '-pull': "pull updates",
        '-restart': "restart after pulled"},
    'usage': "{tr}update [-c|-r] [-pull] [-restart]",
    'examples': [
        "{tr}update : check updates for the whole project",
        "{tr}update -c : check updates for core repo",
        "{tr}update -r : check updates for all plugins repos",
        "{tr}update -pull : pull latest updates to the whole project",
        "{tr}update -pull -restart : auto restart after pulled",
        "{tr}update -c -pull : pull latest updates to the core repo",
        "{tr}update -r -pull : pull latest updates to the plugins repos"]
}, del_pre=True, allow_channels=False)
async def update(message: Message):
    """ check or do updates """
    pull_in_flags = False
    restart_in_flags = False
    core_in_flags = False
    repos_in_flags = False

    flags = list(message.flags)

    if 'pull' in flags:
        pull_in_flags = True
        flags.remove('pull')

        if 'restart' in flags:
            restart_in_flags = True
            flags.remove('restart')

    if 'c' in flags:
        core_in_flags = True
        flags.remove('c')

    if 'r' in flags:
        repos_in_flags = True
        flags.remove('r')

    if flags:
        await message.err("invalid flags")
        return

    await message.edit("`Checking for updates, please wait....`")

    if not core_in_flags and not repos_in_flags:
        core_in_flags = True
        repos_in_flags = True

    updates = ""

    if core_in_flags:
        await api.fetch_core()
        core_updates = await api.get_core_new_commits()

        if core_updates:
            updates += "**Core Updates**\n\n"
            updates += _updates_to_str(core_updates)
            updates += "\n\n"

            if pull_in_flags:
                await api.set_core_version(core_updates[0].version)

    if repos_in_flags:
        await api.fetch_repos()

        for repo_data in await api.get_repos():
            repo_updates = await api.get_repo_new_commits(repo_data.id)

            if repo_updates:
                updates += f"**{repo_data.name} Updates**\n\n"
                updates += _updates_to_str(repo_updates)
                updates += "\n\n"

                if pull_in_flags:
                    await api.set_repo_version(repo_data.id, repo_updates[0].version)

    if updates:
        if pull_in_flags:
            await CHANNEL.log(f"**PULLED updates:\n\n📄 CHANGELOG 📄**\n\n{updates}")

            if restart_in_flags:
                await message.edit("`Restarting [HARD] ...`", del_in=1)
                await userge.restart(hard=True)

            else:
                await message.edit(
                    "updated to latest, "
                    f"do `{config.CMD_TRIGGER}restart -h` to apply changes", del_in=3)
        else:
            await message.edit_or_send_as_file(updates, del_in=0, disable_web_page_preview=True)
    else:
        await message.edit("```no updates found```", del_in=3)


def _updates_to_str(updates: List[Update]) -> str:
    return '\n'.join(
        f"🔨 **#{i.count}** : [{i.summary}]({i.url}) 👷 __{i.author}__" for i in updates)
