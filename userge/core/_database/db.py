# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


from pymongo import MongoClient
from pymongo.collection import Collection

from userge import logging, Config

LOG = logging.getLogger(__name__)
LOG_STR = "$$$>>> __%s__ <<<$$$"

LOG.info(LOG_STR, "Connecting to Database...")

MGCLIENT = MongoClient(Config.DB_URI)


if "Userge" in MGCLIENT.list_database_names():
    LOG.info(LOG_STR, "Userge Database Found :) => Now Logging to it...")

else:
    LOG.info(LOG_STR, "Userge Database Not Found :( => Creating New Database...")


DATABASE = MGCLIENT["Userge"]


def get_collection(name: str) -> Collection:
    """
    Create or Get Collection from your database.
    """

    if name in DATABASE.list_collection_names():
        LOG.debug(LOG_STR, f"{name} Collection Found :) => Now Logging to it...")

    else:
        LOG.debug(LOG_STR, f"{name} Collection Not Found :( => Creating New Collection...")

    return DATABASE[name]
