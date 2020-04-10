from pyrogram import Client


class Base(Client):
    """
    Base Class for Userge.
    """

    def getLogger(self, *args, **kwargs):
        pass

    def getCLogger(self, *args, **kwargs):
        pass

    def new_thread(self, *args, **kwargs):
        pass

    async def get_user_dict(self, *args, **kwargs):
        pass

    def on_cmd(self, *args, **kwargs):
        pass

    def on_new_member(self, *args, **kwargs):
        pass

    def on_left_member(self, *args, **kwargs):
        pass

    def get_help(self, *args, **kwargs):
        pass

    def load_plugin(self, *args, **kwargs):
        pass

    async def reload_plugins(self, *args, **kwargs):
        pass

    def begin(self, *args, **kwargs):
        pass