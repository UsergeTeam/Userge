from .utils import Config, logging
from pyrogram import Client, Filters

logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Userge(Client):

    HELP_DICT = {}

    def __init__(self):
        self.log = logging.getLogger(__name__)

        self.log.info("setting configs...")

        super().__init__(
            Config.HU_STRING_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins = dict(root="userge/plugins")
        )

    def getLogger(self, name: str):
        self.log.info(f"creating new logger => {name}")
        return logging.getLogger(name)

    def on_cmd(self, command: str):
        self.log.info(f"setting new command => {command}")

        def decorator(func):
            dec = self.on_message(Filters.command(command, ".") & Filters.me)
            return dec(func)

        return decorator

    def add_help(self, command: str, about: str):
        self.log.info(f"help dict updated {command} : {about}")
        self.HELP_DICT.update({command: about})

    def get_help(self, key: str = None) -> dict:
        return self.HELP_DICT[key] if key else self.HELP_DICT