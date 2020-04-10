from pyrogram import Client


class Base(Client):
    """
    Base Class for Userge.
    """

    def getCLogger(self, name: str):
        pass