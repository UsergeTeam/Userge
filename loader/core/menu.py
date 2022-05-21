__all__ = ['main_menu']

import os
from time import sleep

from .types import Repos, Sig, Cache


def _clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def _print(out) -> None:
    print(f"{out} !!!")
    sleep(2)


def _invalid(val):
    return input(f"invalid input {val}: ")


def _delete_repos() -> None:
    _clear()

    Repos.load()

    out = ""

    for repo in Repos.iter_repos():
        out += f"{repo.info.id}. {repo.info.url}\n"

    code = input(f"""Menu > settings > repos > delete
0. back
{out.strip()}
: """).strip()

    while True:
        if code == '0':
            _repos()

        else:
            if code.isnumeric() and Repos.get(int(code)):
                Repos.remove(int(code))

                _delete_repos()

            else:
                code = _invalid(code)
                continue

        break


def _core() -> None:
    _clear()

    code = input("""Menu > settings > core
0. back
1. reset
2. invalidate cache
3. clear cache
4. menu
: """).strip()

    while True:
        if code == '0':
            _settings()

        elif code == '1':
            core = Repos.get_core()
            if core:
                core.reset()

            _print("reset core")
            _core()

        elif code == '2' or code == '3':
            Sig.core_remove()

            if code == '2':
                _print("invalidated core cache")

            else:
                Cache.core_remove()

                _print("cleared core cache")

            _core()

        elif code == '4':
            main_menu()

        else:
            code = _invalid(code)
            continue

        break


def _repos() -> None:
    _clear()

    code = input("""Menu > settings > repos
0. back
1. delete
2. invalidate cache
3. clear cache
4. menu
: """).strip()

    while True:
        if code == '0':
            _settings()

        elif code == '1':
            _delete_repos()

        elif code == '2' or code == '3':
            Sig.repos_remove()

            if code == '2':
                _print("invalidated repos cache")

            else:
                Cache.repos_remove()

                _print("cleared repos cache")

            _repos()

        elif code == '4':
            main_menu()

        else:
            code = _invalid(code)
            continue

        break


def _settings() -> None:
    _clear()

    code = input("""Menu > settings
0. back
1. core
2. repos
3. invalidate cache
4. clear cache
: """).strip()

    while True:
        if code == '0':
            main_menu()

        elif code == '1':
            _core()

        elif code == '2':
            _repos()

        elif code == '3' or code == '4':
            Sig.core_remove()
            Sig.repos_remove()

            if code == '3':
                _print("invalidated cache")

            else:
                Cache.core_remove()
                Cache.repos_remove()

                _print("cleared cache")

            _settings()

        else:
            code = _invalid(code)
            continue

        break


def main_menu() -> None:
    _clear()

    code = input("""Menu
1. start
2. settings
3. exit
: """).strip()

    while True:
        if code == '1':
            _clear()

        elif code == '2':
            _settings()

        elif code == '3':
            _clear()
            raise KeyboardInterrupt

        else:
            code = _invalid(code)
            continue

        break
