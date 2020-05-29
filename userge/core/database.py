# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['get_collection']

from pymongo import MongoClient
from pymongo.collection import Collection

from userge import logging, Config

_LOG = logging.getLogger(__name__)
_LOG_STR = "$$$>>> %s <<<$$$"

_LOG.info(_LOG_STR, "Connecting to Database...")

_MGCLIENT = MongoClient(Config.DB_URI)

if "Userge" in _MGCLIENT.list_database_names():
    _LOG.info(_LOG_STR, "Userge Database Found :) => Now Logging to it...")
else:
    _LOG.info(_LOG_STR, "Userge Database Not Found :( => Creating New Database...")

_DATABASE = _MGCLIENT["Userge"]


def get_collection(name: str) -> Collection:
    """Create or Get Collection from your database"""
    if name in _DATABASE.list_collection_names():
        _LOG.debug(_LOG_STR, f"{name} Collection Found :) => Now Logging to it...")
    else:
        _LOG.debug(_LOG_STR, f"{name} Collection Not Found :( => Creating New Collection...")
    return _DATABASE[name]
