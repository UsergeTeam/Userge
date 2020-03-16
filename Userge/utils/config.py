import os
from dotenv import load_dotenv
from .logger import logging

log = logging.getLogger(__name__)

config_file = "config.env"

if os.path.isfile(config_file):
    log.info(f"{config_file} Found and loading ...")
    load_dotenv(config_file)

if os.environ.get("_____REMOVE_____THIS_____LINE_____", None):
    log.error("Please remove the line mentioned in the first hashtag from the config.env file")
    quit(1)


class Config:
    API_ID = int(os.environ.get("API_ID", 12345))

    API_HASH = os.environ.get("API_HASH", None)

    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)

    DB_URI = os.environ.get("DATABASE_URL", None)
