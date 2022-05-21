from importlib import import_module
from os import execl
from sys import executable


if __name__ == '__main__':
    try:
        getattr(import_module("loader.core.main"), 'load')()
    except InterruptedError:
        execl(executable, executable, '-m', 'loader')
        raise SystemExit
