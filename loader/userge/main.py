from importlib import import_module
from os.path import abspath
from sys import argv


def run(conn) -> None:
    argv[0] = abspath("userge")
    getattr(import_module("loader.userge.connection"), '_set')(conn)
    getattr(getattr(import_module("userge.main"), 'userge'), 'begin')()
