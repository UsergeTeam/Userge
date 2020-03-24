from pymongo import MongoClient
from pymongo.collection import Collection
from userge.utils import Config, logging

LOG = logging.getLogger(__name__)

DB_MAIN_STRING = "$$$>>> __{}__ <<<$$$"

LOG.info(
    DB_MAIN_STRING.format("Connecting to Database..."))

MGCLIENT = MongoClient(Config.DB_URI)


if "Userge" in MGCLIENT.list_database_names():
    LOG.info(
        DB_MAIN_STRING.format("Userge Database Found :) => Now Logging to it..."))

else:
    LOG.info(
        DB_MAIN_STRING.format("Userge Database Not Found :( => Creating New Database..."))


DATABASE = MGCLIENT["Userge"]


def get_collection(name: str) -> Collection:
    """
    Create or Get Collection from your database.
    """
    
    if name in DATABASE.list_collection_names():
        LOG.info(
            DB_MAIN_STRING.format(f"{name} Collection Found :) => Now Logging to it..."))

    else:
        LOG.info(
            DB_MAIN_STRING.format(f"{name} Collection Not Found :( => Creating New Collection..."))

    return DATABASE[name]
