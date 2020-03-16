from .utils import Config, logging

log = logging.getLogger(__name__)


from pyrogram import Client, Filters

logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Userge(Client):

    HELP_DICT = {}
    LOG = logging

    def __init__(self):
        self.log = log
        log.info("setting configs...")
        super().__init__(
            Config.HU_STRING_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins = dict(root="Userge/plugins")
        )

    def getLogger(self, name: str):
        log.info(f"creating new logger => {name}")
        return self.LOG.getLogger(name)

    def cmd(self, command: str):
        log.info(f"setting new command => {command}")
        return Filters.command(command, ".") & Filters.me

    def add_help(self, command: str, about: str):
        log.info(f"help dict updated {command} : {about}")
        self.HELP_DICT.update({command: about})

    def get_help(self, key: str = None) -> dict:
        return self.HELP_DICT[key] if key else self.HELP_DICT