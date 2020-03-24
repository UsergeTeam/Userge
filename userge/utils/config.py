import os
from dotenv import load_dotenv
from .logger import logging

LOG = logging.getLogger(__name__)

CONFIG_FILE = "config.env"

if os.path.isfile(CONFIG_FILE):
    LOG.info(f"{CONFIG_FILE} Found and loading ...")
    load_dotenv(CONFIG_FILE)

if os.environ.get("_____REMOVE_____THIS_____LINE_____", None):
    LOG.error("Please remove the line mentioned in the first hashtag from the config.env file")
    quit(1)


class Config:
    API_ID = int(os.environ.get("API_ID", 12345))

    API_HASH = os.environ.get("API_HASH", None)

    HU_STRING_SESSION = os.environ.get("HU_STRING_SESSION", None)

    DB_URI = os.environ.get("DATABASE_URL", None)

    MAX_MESSAGE_LENGTH = 4096

    LANG = os.environ.get("PREFERRED_LANGUAGE", "en")

    DOWN_PATH = "./downloads/"
