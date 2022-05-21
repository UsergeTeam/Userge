__all__ = ['log', 'error', 'terminate', 'call', 'open_url', 'get_client_type',
           'safe_url', 'safe_repo_info', 'grab_conflicts', 'assert_read', 'assert_write',
           'assert_read_write', 'remove', 'rmtree', 'clean_core', 'clean_plugins', 'print_logo']

import logging
import os
import re
import stat
import subprocess
from copy import copy
from functools import lru_cache
from itertools import combinations
from logging.handlers import RotatingFileHandler
from os.path import join
from shutil import rmtree as _rmtree
from typing import Optional, Tuple, Set, Dict, Any
from urllib.error import HTTPError
from urllib.request import urlopen, Request
try:
    from signal import CTRL_C_EVENT as SIGTERM
except ImportError:
    from signal import SIGTERM

from loader.types import RepoInfo

if not os.path.exists('logs'):
    os.mkdir('logs')

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        RotatingFileHandler(
                            "logs/loader.log", maxBytes=81920, backupCount=10),
                        logging.StreamHandler()
                    ])

_LOG = logging.getLogger("loader")


def log(msg: str) -> None:
    _LOG.info(msg)


def error(msg: str, hint: Optional[str] = None, interrupt=True) -> None:
    _LOG.error(msg + "\n\tHINT: " + hint if hint else msg)
    if interrupt:
        raise KeyboardInterrupt


def terminate(pid: int) -> None:
    os.kill(pid, SIGTERM)


def call(*args: str) -> Tuple[int, str]:
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return p.wait(), p.communicate()[1]


def open_url(url: str, headers: Optional[dict] = None) -> Tuple[Any, Optional[str]]:
    r = Request(url, headers=headers or {})
    try:
        return urlopen(r, timeout=3), None
    except HTTPError as e:
        return e.code, e.reason


def get_client_type() -> str:
    token = os.environ.get('BOT_TOKEN')
    string = os.environ.get('SESSION_STRING')

    if token and string:
        return "dual"
    if token:
        return "bot"
    if string:
        return "user"


_TOKEN = re.compile("ghp_[0-9A-z]{36}")
_REQUIREMENTS = re.compile(r'(\S+)(<=|<|==|>=|>|!=|~=)(\S+)')


@lru_cache
def safe_url(url: str) -> str:
    return _TOKEN.sub('private', url)


def safe_repo_info(repo_info: RepoInfo) -> RepoInfo:
    info = copy(repo_info)
    info.url = safe_url(info.url)

    return info


def grab_conflicts(requirements: Set[str]) -> Set[str]:
    to_audit: Dict[str, Dict[str, Set[str]]] = {}

    for req in filter(lambda _: any(map(_.__contains__, ('=', '>', '<'))), requirements):
        match = _REQUIREMENTS.match(req)

        name = match.group(1)
        cond = match.group(2)
        version = match.group(3)

        if name not in to_audit:
            to_audit[name] = {}

        versions = to_audit[name]

        if version not in versions:
            versions[version] = set()

        version = versions[version]

        # :)
        if cond == '~=':
            cond = '>='

        version.add(cond)

    gt, ge, eq, le, lt, neq = '>', '>=', '==', '<=', '<', '!='

    sequence = (
        (gt, ge, neq),
        (ge, eq, le),
        (le, lt, neq)
    )

    pattern = []

    for i in range(len(sequence)):
        seq = sequence[i]

        pattern.append(seq)
        pattern.extend(combinations(seq, 2))

        for j in range(i + 1):
            pattern.append((seq[j],))

    pattern = tuple(pattern)

    for name, versions in to_audit.items():
        found = False

        for version in sorted(versions, reverse=True):
            args = versions[version]

            if found:
                # find and remove compatible reqs
                for _ in sequence[0]:
                    if _ in args:
                        args.remove(_)
            else:
                for check in pattern:
                    if all(map(args.__contains__, check)):
                        # found the breakpoint
                        for _ in check:
                            args.remove(_)

                        if not any(map(check.__contains__, sequence[2])):
                            found = True

                        break

    conflicts = set()

    for name, versions in to_audit.items():
        for version, args in versions.items():
            for arg in args:
                conflicts.add(name + arg + version)

    return conflicts


def _perm(path: str, check: Optional[int], perm: int) -> bool:
    return bool(check and os.access(path, check) or os.chmod(path, perm))


def assert_read(path: str) -> bool:
    return _perm(path, os.R_OK, stat.S_IREAD)


def assert_write(path: str, force=False) -> bool:
    return _perm(path, None if force else os.W_OK, stat.S_IWRITE)


def assert_read_write(path: str) -> bool:
    return _perm(path, os.R_OK | os.W_OK, stat.S_IREAD | stat.S_IWRITE)


def _on_error(func, path, _) -> None:
    if os.path.exists(path) and not assert_write(path):
        func(path)


def remove(path: str) -> None:
    if os.path.exists(path):
        assert_write(path)
        os.remove(path)


def rmtree(path: str) -> None:
    if os.path.isdir(path):
        _rmtree(path, onerror=_on_error)


def clean_core() -> None:
    rmtree("userge")


def clean_plugins() -> None:
    plugins_path = join("userge", "plugins")

    for cat in os.listdir(plugins_path):
        if cat == "builtin":
            continue

        rmtree(join(plugins_path, cat))


def _print_line():
    log('->- ->- ->- ->- ->- ->- ->- --- -<- -<- -<- -<- -<- -<- -<-')


def print_logo():
    _print_line()

    logo = r'''
     ________            __  __               ______
    /_  __/ /_  ___     / / / /_______  _____/ ____/__
     / / / __ \/ _ \   / / / / ___/ _ \/ ___/ / __/ _ \
    / / / / / /  __/  / /_/ (__  )  __/ /  / /_/ /  __/
   /_/ /_/ /_/\___/   \____/____/\___/_/   \____/\___/
'''
    log(logo)

    _print_line()
