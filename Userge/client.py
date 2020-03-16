from .utils import Config, logging

log = logging.getLogger(__name__)


from pyrogram import Client

logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Userge(Client):
    def __init__(self):
        super().__init__(
            Config.HU_STRING_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins = dict(root="Userge/plugins")
        )