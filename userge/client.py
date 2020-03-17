from .utils import Config, logging
from pyrogram import Client, Filters, Message

logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Userge(Client):
    HELP_DICT = {}
    USERGE_MAIN_STRING = "<<<!  #####  ___{}___  #####  !>>>"
    USERGE_SUB_STRING = "<<<!  {}  !>>>"
    MSG = Message

    def __init__(self):
        self.log = logging.getLogger(__name__)

        self.log.info(self.USERGE_MAIN_STRING.format("Setting Userge Configs"))

        super().__init__(
            Config.HU_STRING_SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="userge/plugins")
        )

    def getLogger(self, name: str):
        self.log.info(self.USERGE_SUB_STRING.format(f"Creating Logger => {name}"))
        return logging.getLogger(name)

    def on_cmd(self, command: str, about: str):
        self.__add_help(command, about)

        def decorator(func):
            self.log.info(self.USERGE_SUB_STRING.format(
                f"Loading => [ async def {func.__name__}(client, message) ] On .{command} Command"))
            dec = self.on_message(Filters.regex(pattern=f"^.{command}") & Filters.me)

            return dec(func)

        return decorator

    def __add_help(self, command: str, about: str):
        self.log.info(self.USERGE_SUB_STRING.format(f"Updating Help Dict => [ {command} : {about} ]"))
        self.HELP_DICT.update({command: about})

    def get_help(self, key: str = None) -> dict:
        return self.HELP_DICT[key] if key else self.HELP_DICT

    def begin(self):
        self.log.info(self.USERGE_MAIN_STRING.format("Starting Userge"))
        self.run()
        self.log.info(self.USERGE_MAIN_STRING.format("Exiting Userge"))
