__all__ = [
    'restart',
    'fetch_core',
    'fetch_repo',
    'fetch_repos',
    'get_core',
    'get_repo',
    'get_repos',
    'add_repo',
    'remove_repo',
    'get_core_new_commits',
    'get_core_old_commits',
    'get_repo_new_commits',
    'get_repo_old_commits',
    'edit_core',
    'set_core_branch',
    'set_core_version',
    'edit_repo',
    'set_repo_branch',
    'set_repo_version',
    'set_repo_priority',
    'add_constraints',
    'remove_constraints',
    'get_constraints',
    'clear_constraints',
    'invalidate_repos_cache',
    'set_env',
    'unset_env']

from typing import List, Optional, Union

from loader.job import *
from loader.types import RepoInfo, Update, Constraint
from .connection import send_and_wait, send_and_async_wait


def restart(hard: bool = False) -> None:
    """
    terminate the current process and start new process
    Args:
        hard: if False the initialization things will be ignored. default to False.
    """
    send_and_wait(HARD_RESTART if hard else SOFT_RESTART)


async def fetch_core() -> None:
    """
    fetch data from the default remote and update the local core repository.
    """
    return await send_and_async_wait(FETCH_CORE)


async def fetch_repo(repo_id: int) -> None:
    """
    fetch data from the default remote and update this local plugins repository.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()
    """
    return await send_and_async_wait(FETCH_REPO, repo_id)


async def fetch_repos() -> None:
    """
    fetch data from the default remote and update all the local plugins repositories.
    """
    return await send_and_async_wait(FETCH_REPOS)


async def get_core() -> Optional[RepoInfo]:
    """
    get the core repo details.
    Returns:
        details as a RepoInfo object.
    """
    return await send_and_async_wait(GET_CORE)


async def get_repo(repo_id: int) -> Optional[RepoInfo]:
    """
    get details of the plugins repos.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()

    Returns:
        RepoInfo objects.
    """
    return await send_and_async_wait(GET_REPO, repo_id)


async def get_repos() -> List[RepoInfo]:
    """
    get details of all the plugins repos.
    Returns:
        list of RepoInfo objects.
    """
    return await send_and_async_wait(GET_REPOS)


async def add_repo(priority: int, branch: str, url: str) -> bool:
    """
    add a plugins repo.
    Args:
        priority: priority of this repo. using this number the loader will sort the repos list.
            the loader will override plugins with the same name. so if you don't want to override
            the plugins of this repo then use higher priority.
        branch: branch name of this repo.
        url: link to the repo

    Returns:
        True if success and else False.
    """
    return await send_and_async_wait(ADD_REPO, priority, branch, url)


async def remove_repo(repo_id: int) -> bool:
    """
    remove a plugins repo by its id.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()

    Returns:
        True if success and else False.
    """
    return await send_and_async_wait(REMOVE_REPO, repo_id)


async def get_core_new_commits() -> Optional[List[Update]]:
    """
    get new commits to the current branch of core repo compared to the current version.
    Returns:
        list of Update objects.
    """
    return await send_and_async_wait(GET_CORE_NEW_COMMITS)


async def get_core_old_commits(limit: int) -> Optional[List[Update]]:
    """
    get old commits from the current branch of core repo compared to the current version.
    Args:
        limit: specify how many commits you want.

    Returns:
        list of Update objects.
    """
    return await send_and_async_wait(GET_CORE_OLD_COMMITS, limit)


async def get_repo_new_commits(repo_id: int) -> Optional[List[Update]]:
    """
    get new commits to the current branch of plugins repo compared to the current version.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()

    Returns:
        list of Update objects.
    """
    return await send_and_async_wait(GET_REPO_NEW_COMMITS, repo_id)


async def get_repo_old_commits(repo_id: int, limit: int) -> Optional[List[Update]]:
    """
    get old commits from the current branch of plugins repo compared to the current version.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()
        limit: specify how many commits you want.

    Returns:
        list of Update objects.
    """
    return await send_and_async_wait(GET_REPO_OLD_COMMITS, repo_id, limit)


async def edit_core(branch: Optional[str], version: Optional[Union[int, str]]) -> bool:
    """
    edit the core repo branch and version.
    Args:
        branch: branch name. hint: get_core() to see available branches.
            if None stay as same.
        version: version as hash or id. hint: get_core_new_commits() or get_core_old_commits().
            if None stay as same.

    Returns:
        True if changed.
    """
    return await send_and_async_wait(EDIT_CORE, branch, version)


async def set_core_branch(branch: str) -> bool:
    """
    change the core repo branch.
    Args:
        branch: branch name. hint: get_core() to see available branches.

    Returns:
        True if changed.
    """
    return await edit_core(branch, None)


async def set_core_version(version: Union[int, str]) -> bool:
    """
    change the core repo version.
    Args:
        version: version as hash or id. hint: get_core_new_commits() or get_core_old_commits().

    Returns:
        True if changed.
    """
    return await edit_core(None, version)


async def edit_repo(repo_id: int, branch: Optional[str],
                    version: Optional[Union[int, str]], priority: Optional[int]) -> bool:
    """
    edit the plugins repo branch, version and priority.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos().
            if None stay as same.
        branch: branch name. hint: get_repos() to see available branches.
            if None stay as same.
        version: version as hash or id. hint: get_repo_new_commits() or get_repo_old_commits().
            if None stay as same.
        priority: priority of this repo. hint: see docs of add_repo().
            if None stay as same.

    Returns:
        True if changed.
    """
    return await send_and_async_wait(EDIT_REPO, repo_id, branch, version, priority)


async def set_repo_branch(repo_id: int, branch: str) -> bool:
    """
    change the plugins repo branch.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()
        branch: branch name. hint: get_repos() to see available branches.

    Returns:
        True if changed.
    """
    return await edit_repo(repo_id, branch, None, None)


async def set_repo_version(repo_id: int, version: Union[int, str]) -> bool:
    """
    change the plugins repo version.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()
        version: version as hash or id. hint: get_repo_new_commits() or get_repo_old_commits().

    Returns:
        True if changed.
    """
    return await edit_repo(repo_id, None, version, None)


async def set_repo_priority(repo_id: int, priority: int) -> bool:
    """
    change the plugins repo priority.
    Args:
        repo_id: id from the RepoInfo object. hint: get_repos()
        priority: priority of this repo. hint: see docs of add_repo().

    Returns:
        True if changed.
    """
    return await edit_repo(repo_id, None, None, priority)


async def add_constraints(c_type: str, data: List[str]) -> bool:
    """
    add constraints to filter plugins or categories.
    Args:
        c_type: constraint type which can be `include`, `exclude` or `in`. the sequence of the
            filter process is, first check for `include` constraints. if found then
            the filter process will be terminated and the plugins or the categories
            will be added to the project. if not found (`include`) then the loader will check
            for `exclude` constraints. if found then those plugins or categories will be ignored.
            if not found (`exclude`) then the loader will check for `in` constraints. if found
            then the loader will add only plugins and categories in this constraint. other all
            things will be ignored.
        data: list of constraints. a constraint can be
            a plugin name (ping),
            a category name (admin/),
            a repo name followed by a plugin name (usergeteam.userge-plugins/ping) and
            a repo name followed by a category name (usergeteam.userge-plugins/admin/).

    Returns:
        True if success and else False.
    """
    return await send_and_async_wait(ADD_CONSTRAINTS, c_type, data)


async def remove_constraints(c_type: Optional[str], data: List[str]) -> bool:
    """
    remove added constraints.
    Args:
        c_type: constraint type. hint: see docs of add_constraints().
            if None then all the given constraint data will be removed without considering
            the constraint type. if its there, then it will limit to the constraint type.
        data: list of constraints. hint: see docs of add_constraints().

    Returns:
        True if success and else False.
    """
    return await send_and_async_wait(REMOVE_CONSTRAINTS, c_type, data)


async def get_constraints() -> List[Constraint]:
    """
    get all added constraints.
    Returns:
        list of Constraint objects.
    """
    return await send_and_async_wait(GET_CONSTRAINTS)


async def clear_constraints(c_type: Optional[str]) -> bool:
    """
    clear all added constraints.
    Args:
        c_type: constraint type. hint: see docs of add_constraints(). if None then this will
            clear the all constraints. else, the constraint only related to this type
            will be cleared.

    Returns:
        True if success and else False.
    """
    return await send_and_async_wait(CLEAR_CONSTRAINTS, c_type)


async def invalidate_repos_cache() -> None:
    """
    notify the loader that the plugins should re-initialize.
    """
    return await send_and_async_wait(INVALIDATE_REPOS_CACHE)


async def set_env(key: str, value: str) -> None:
    """
    set an environment variable.
    Args:
        key: key of the var
        value: value of the var
    """
    return await send_and_async_wait(SET_ENV, key, value)


async def unset_env(key: str) -> None:
    """
    remove an environment variable.
    Args:
        key: key of the var
    """
    return await send_and_async_wait(UNSET_ENV, key)
