# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ["LogBot"]


def _log(func):
    def wrapper(text, log=None, tmp=None):
        if log and callable(log):
            if tmp:
                log(tmp, text)
            else:
                log(text)
        func(text)
    return wrapper


class LogBot:
    """ Bot Logger """
    _CONN = "logs/logbot.stdin"

    @staticmethod
    def _send_data(*args) -> None:
        with open(LogBot._CONN, 'a') as l_b:
            l_b.write(f"{' '.join(args)}\n")

    @staticmethod
    def end() -> None:
        """ end bot session """
        LogBot._send_data("quit")

    @staticmethod
    def cleanup() -> None:
        """ cleanup bot session """
        LogBot.del_all_msgs()
        LogBot.end()

    @staticmethod
    @_log
    def send_msg(text: str, log=None, tmp=None) -> None:  # pylint: disable=unused-argument
        """ send message """
        LogBot._send_data("sendMessage", text)

    @staticmethod
    @_log
    def reply_last_msg(text: str, log=None, tmp=None) -> None:  # pylint: disable=unused-argument
        """ reply to last message """
        LogBot._send_data("replyLastMessage", text)

    @staticmethod
    @_log
    def edit_last_msg(text: str, log=None, tmp=None) -> None:  # pylint: disable=unused-argument
        """ edit last message """
        LogBot._send_data("editLastMessage", text)

    @staticmethod
    def del_last_msg() -> None:
        """ delete last message """
        LogBot._send_data("deleteLastMessage")

    @staticmethod
    def del_all_msgs() -> None:
        """ delete all messages """
        LogBot._send_data("deleteMessages")

    @staticmethod
    def print_all_msgs() -> None:
        """ print all messages """
        LogBot._send_data("printMessages")
