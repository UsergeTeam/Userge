__all__ = ['do_checks']

import atexit
import json
import os
import sys
from base64 import urlsafe_b64decode
from os.path import exists, isfile
from shutil import which
from struct import unpack, error as struct_error

from dotenv import load_dotenv
from pymongo import MongoClient

from . import MIN_PY, MAX_PY, CONF_PATH
from .types import Database
from .utils import log, error, open_url, assert_read, assert_read_write

atexit.register(lambda _: exists(_) and assert_read_write(_), CONF_PATH)


def _git() -> None:
    log("Checking Git ...")

    if not which("git"):
        error("Required git !", "install git")


def _py_version() -> None:
    log("Checking Python Version ...")

    py_ver = sys.version_info[0] + sys.version_info[1] / 10

    if py_ver < MIN_PY:
        error(f"You MUST have a python version of at least {MIN_PY}.0 !",
              "upgrade your python version")

    if py_ver > MAX_PY:
        error(f"You MUST have a python version of at most {MAX_PY} !",
              "downgrade your python version")

    log(f"\tFound PYTHON - v{py_ver}.{sys.version_info[2]} ...")


def _config_file() -> None:
    log("Checking Config File ...")

    if isfile(CONF_PATH):
        log(f"\tConfig file found : {CONF_PATH}, Exporting ...")

        assert_read(CONF_PATH)
        load_dotenv(CONF_PATH)


def _vars() -> None:
    log("Checking ENV Vars ...")

    env = os.environ

    string = env.get('SESSION_STRING')

    if env.get('HU_STRING_SESSION') and not string:
        error("Deprecated HU_STRING_SESSION var !", "its SESSION_STRING now")

    for _ in ('API_ID', 'API_HASH', 'DATABASE_URL', 'LOG_CHANNEL_ID'):
        val = env.get(_)

        if not val:
            error(f"Required {_} var !")

    log_channel = env.get('LOG_CHANNEL_ID')

    if not log_channel.startswith("-100") or not log_channel[1:].isnumeric():
        error(f"Invalid LOG_CHANNEL_ID {log_channel} !", "it should startswith -100")

    bot_token = env.get('BOT_TOKEN')

    if not string and not bot_token:
        error("Required SESSION_STRING or BOT_TOKEN var !")

    if string:
        if len(string) == 351:
            str_fmt = ">B?256sI?"
        elif len(string) == 356:
            str_fmt = ">B?256sQ?"
        else:
            str_fmt = ">BI?256sQ?"

        try:
            unpack(str_fmt, urlsafe_b64decode(string + "=" * (-len(string) % 4)))
        except struct_error:
            error("Invalid SESSION_STRING var !", "need a pyrogram session string")

    if bot_token:
        if ':' not in bot_token:
            error("Invalid BOT_TOKEN var !", "get it from @botfather")

        if not env.get('OWNER_ID'):
            error("Required OWNER_ID var !", "set your id to this")

    _var_data = dict(
        DOWN_PATH="downloads",
        ASSERT_SINGLE_INSTANCE="false",
        CMD_TRIGGER='.',
        SUDO_TRIGGER='!',
        FINISHED_PROGRESS_STR='█',
        UNFINISHED_PROGRESS_STR='░'
    )
    for k, v in _var_data.items():
        env.setdefault(k, v)

    workers = int(env.get('WORKERS') or 0)
    env['WORKERS'] = str(min(16, max(workers, 0) or os.cpu_count() + 4, os.cpu_count() + 4))
    env['MOTOR_MAX_WORKERS'] = env['WORKERS']

    down_path = env['DOWN_PATH']
    env['DOWN_PATH'] = down_path.rstrip('/') + '/'

    cmd_trigger = env['CMD_TRIGGER']
    sudo_trigger = env['SUDO_TRIGGER']

    if len(cmd_trigger) != 1 or len(sudo_trigger) != 1:
        error(f"Too large CMD_TRIGGER ({cmd_trigger}) or SUDO_TRIGGER ({sudo_trigger})",
              "trigger should be a single character")

    if cmd_trigger == sudo_trigger:
        error(f"Invalid SUDO_TRIGGER!, You can't use {cmd_trigger} as SUDO_TRIGGER",
              "use diff triggers for cmd and sudo triggers")

    if cmd_trigger == '/' or sudo_trigger == '/':
        error("You can't use / as CMD_TRIGGER or SUDO_TRIGGER", "try diff one")

    h_api = 'HEROKU_API_KEY'
    h_app = 'HEROKU_APP_NAME'

    if not env.get('DYNO'):
        for _ in (h_api, h_app):
            if _ in env:
                env.pop(_)

    h_api = env.get(h_api)
    h_app = env.get(h_app)

    if h_api and not h_app or not h_api and h_app:
        error("Need both HEROKU_API_KEY and HEROKU_APP_NAME vars !")

    if h_api and h_app:
        if len(h_api) != 36 or len(h_api.split('-')) != 5:
            error(f"Invalid HEROKU_API_KEY ({h_api}) !")

        headers = {
            'Accept': "application/vnd.heroku+json; version=3",
            'Authorization': f"Bearer {h_api}"
        }

        r, e = open_url("https://api.heroku.com/account/rate-limits", headers)
        if e:
            error(f"Invalid HEROKU_API_KEY, {r} > {e}")

        r, e = open_url(f"https://api.heroku.com/apps/{h_app}", headers)
        if e:
            error(f"Couldn't find heroku app ({h_app}), {r} > {e}",
                  "either name invalid or api key from diff account")

    if Database.is_none():
        db_url = env.get('DATABASE_URL')

        try:
            new_url = Database.fix_url(db_url)
        except ValueError:
            error(f"Invalid DATABASE_URL > ({db_url}) !")
            return

        if new_url != db_url:
            env['DATABASE_URL'] = new_url

        cl = MongoClient(new_url, maxPoolSize=1, minPoolSize=0)

        try:
            cl.list_database_names()
        except Exception as e:
            error(f"Invalid DATABASE_URL > {str(e)}")

        Database.set(cl)

    if bot_token:
        api_url = "https://api.telegram.org/bot" + bot_token

        e = open_url(api_url + "/getMe")[1]

        if e:
            error("Invalid BOT_TOKEN var !", "get or revoke it from @botfather")

        r, e = open_url(api_url + "/getChat?chat_id=" + log_channel)

        if e:
            if r == 400:
                error(f"Invalid LOG_CHANNEL_ID ({log_channel}) !",
                      "add your bot to log chat if this value is ok")

            if r == 403:
                error("Bot not found in log chat !", "add bot to your log chat as admin")

            error(f"Unknown error [getChat] ({r}) {e} !", "ask @usergeot")

        result = json.loads(r.read())['result']

        chat_type = result.get('type')
        chat_username = result.get('username')

        if chat_type not in ('supergroup', 'channel'):
            error(f"Invalid log chat type ({chat_type}) !",
                  "only supergroups and channels are supported")

        if chat_username:
            error(f"Can't use a public log chat (@{chat_username}) !", "make it private")

    for _ in (down_path, '.rcache'):
        os.makedirs(_, exist_ok=True)


def do_checks() -> None:
    _git()
    _py_version()
    _config_file()
    _vars()
