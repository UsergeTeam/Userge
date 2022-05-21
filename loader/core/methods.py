__all__ = ['fetch_core', 'fetch_repos']

from contextlib import suppress
from os import environ
from typing import List, Optional, Callable, Union

from dotenv import set_key, unset_key

from . import CONF_PATH
from .types import Tasks, Session, Repos, Constraints, Sig
from .utils import error, safe_repo_info
from .. import job
from ..types import RepoInfo, Update, Constraint


def on(work: int) -> Callable[[Callable], Callable]:
    def wrapper(func: Callable) -> Callable:
        Tasks.add(work, func)
        return func

    return wrapper


@on(job.SOFT_RESTART)
def restart_soft() -> None:
    Session.restart(False)


@on(job.HARD_RESTART)
def restart_hard() -> None:
    Session.restart(True)


@on(job.FETCH_CORE)
def fetch_core() -> None:
    core = Repos.get_core()
    if not core:
        error("Core Not Found !")

    core.init()
    core.fetch()


@on(job.FETCH_REPO)
def fetch_repo(repo_id: int) -> None:
    repo = Repos.get(repo_id)
    if repo:
        repo.init()
        repo.fetch()


@on(job.FETCH_REPOS)
def fetch_repos() -> None:
    for repo in Repos.iter_repos():
        repo.init()
        repo.fetch()


@on(job.GET_CORE)
def get_core() -> Optional[RepoInfo]:
    core = Repos.get_core()
    if core:
        return core.info


@on(job.GET_REPO)
def get_repo(repo_id: int) -> Optional[RepoInfo]:
    repo = Repos.get(repo_id)
    if repo:
        return safe_repo_info(repo.info)


@on(job.GET_REPOS)
def get_repos() -> List[RepoInfo]:
    data = []

    for repo in Repos.iter_repos():
        data.append(safe_repo_info(repo.info))

    return data


@on(job.ADD_REPO)
def add_repo(priority: int, branch: str, url: str) -> bool:
    return Repos.add(priority, branch, url)


@on(job.REMOVE_REPO)
def remove_repo(repo_id: int) -> bool:
    return Repos.remove(repo_id)


@on(job.GET_CORE_NEW_COMMITS)
def get_core_new_commits() -> Optional[List[Update]]:
    core = Repos.get_core()
    if core:
        return core.new_commits()


@on(job.GET_CORE_OLD_COMMITS)
def get_core_old_commits(limit: int) -> Optional[List[Update]]:
    core = Repos.get_core()
    if core:
        return core.old_commits(limit)


@on(job.GET_REPO_NEW_COMMITS)
def get_repo_new_commits(repo_id: int) -> Optional[List[Update]]:
    repo = Repos.get(repo_id)
    if repo:
        return repo.new_commits()


@on(job.GET_REPO_OLD_COMMITS)
def get_repo_old_commits(repo_id: int, limit: int) -> Optional[List[Update]]:
    repo = Repos.get(repo_id)
    if repo:
        return repo.old_commits(limit)


@on(job.EDIT_CORE)
def edit_core(branch: Optional[str], version: Optional[Union[int, str]]) -> bool:
    core = Repos.get_core()
    if core:
        return core.edit(branch, version)

    return False


@on(job.EDIT_REPO)
def edit_repo(repo_id: int, branch: Optional[str], version: Optional[Union[int, str]],
              priority: Optional[int]) -> bool:
    repo = Repos.get(repo_id)
    if repo:
        return repo.edit(branch, version, priority)

    return False


@on(job.ADD_CONSTRAINTS)
def add_constraints(c_type: str, data: List[str]) -> bool:
    return Constraints.add(c_type, data)


@on(job.REMOVE_CONSTRAINTS)
def remove_constraints(c_type: Optional[str], data: List[str]) -> bool:
    return Constraints.remove(c_type, data)


@on(job.GET_CONSTRAINTS)
def get_constraints() -> List[Constraint]:
    return Constraints.get()


@on(job.CLEAR_CONSTRAINTS)
def clear_constraints(c_type: Optional[str]) -> bool:
    return Constraints.clear(c_type)


@on(job.INVALIDATE_REPOS_CACHE)
def invalidate_repos_cache() -> None:
    Sig.repos_remove()


@on(job.SET_ENV)
def set_env(key: str, value: str) -> None:
    set_key(CONF_PATH, key, value)
    if key not in environ:
        Sig.repos_remove()

    environ[key] = value


@on(job.UNSET_ENV)
def unset_env(key: str) -> None:
    unset_key(CONF_PATH, key)
    with suppress(KeyError):
        del environ[key]
        Sig.repos_remove()
