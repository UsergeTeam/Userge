# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2021 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

__all__ = ['Message']

import re
import asyncio
from contextlib import contextmanager
from typing import List, Dict, Tuple, Union, Optional, Sequence, Callable, Any

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message as RawMessage
from pyrogram.errors import (
    MessageAuthorRequired, MessageTooLong, MessageNotModified,
    MessageIdInvalid, MessageDeleteForbidden, BotInlineDisabled
)

from userge import logging, Config
from userge.utils import is_command
from ... import client as _client  # pylint: disable=unused-import

_CANCEL_CALLBACKS: Dict[str, List[Callable[[], Any]]] = {}
_ERROR_STRING = "**ERROR**: `{}`"
_ERROR_MSG_DELETE_TIMEOUT = 5

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  :::::  %s  :::::  !>>>"


class Message(RawMessage):
    """ Modded Message Class For Userge """
    def __init__(self,
                 client: Union['_client.Userge', '_client.UsergeBot'],
                 mvars: Dict[str, object], module: str, **kwargs: Union[str, bool]) -> None:
        self._filtered = False
        self._filtered_input_str = ''
        self._flags: Dict[str, str] = {}
        self._process_canceled = False
        self._module = module
        self._kwargs = kwargs
        super().__init__(client=client, **mvars)

    @classmethod
    def parse(cls, client: Union['_client.Userge', '_client.UsergeBot'],
              message: RawMessage, **kwargs: Union[str, bool]) -> 'Message':
        """ parse message """
        mvars = vars(message)
        for key_ in ['_client', '_filtered', '_filtered_input_str',
                     '_flags', '_process_canceled', '_module', '_kwargs']:
            if key_ in mvars:
                del mvars[key_]
        if mvars['reply_to_message']:
            mvars['reply_to_message'] = cls.parse(client, mvars['reply_to_message'], **kwargs)
        return cls(client, mvars, **kwargs)

    @property
    def client(self) -> Union['_client.Userge', '_client.UsergeBot']:
        """ returns client """
        return self._client

    @property
    def input_raw(self) -> str:
        """ Returns the input string without command as raw """
        input_ = self.text.html if hasattr(self.text, 'html') else self.text
        if ' ' in input_ or '\n' in input_:
            return str(input_.split(maxsplit=1)[1].strip())
        return ''

    @property
    def input_str(self) -> str:
        """ Returns the input string without command """
        input_ = self.text
        if ' ' in input_ or '\n' in input_:
            return str(input_.split(maxsplit=1)[1].strip())
        return ''

    @property
    def input_or_reply_raw(self) -> str:
        """ Returns the input string  or replied msg text without command as raw """
        input_ = self.input_raw
        if not input_ and self.reply_to_message:
            input_ = (
                self.reply_to_message.text.html if self.reply_to_message.text else
                self.reply_to_message.caption.html if self.reply_to_message.caption else ''
            ).strip()
        return input_

    @property
    def input_or_reply_str(self) -> str:
        """ Returns the input string  or replied msg text without command """
        input_ = self.input_str
        if not input_ and self.reply_to_message:
            input_ = (self.reply_to_message.text or self.reply_to_message.caption or '').strip()
        return input_

    @property
    def filtered_input_str(self) -> str:
        """ Returns the filtered input string without command and flags """
        self._filter()
        return self._filtered_input_str

    @property
    def flags(self) -> Dict[str, str]:
        """ Returns all flags in input string as `Dict` """
        self._filter()
        return self._flags

    @property
    def process_is_canceled(self) -> bool:
        """ Returns True if process canceled """
        return self._process_canceled

    @property
    def extract_user_and_text(self) -> Tuple[Optional[Union[str, int]], Optional[str]]:
        """ Extracts User and Text
        [NOTE]: This method checks for reply first.
        On Success:
            user (``str | int | None``) and text (``str | None``)
        """
        user_e: Optional[Union[str, int]] = None
        text: Optional[str] = None
        if self.reply_to_message:
            if self.reply_to_message.from_user:
                user_e = self.reply_to_message.from_user.id
            text = self.filtered_input_str
            return user_e, text
        if self.filtered_input_str:
            data = self.filtered_input_str.split(maxsplit=1)
            # Grab First Word and Process it.
            if len(data) == 2:
                user, text = data
            elif len(data) == 1:
                user = data[0]
            # if user id, convert it to integer
            if user.isdigit():
                user_e = int(user)
            elif self.entities:
                # Extracting text mention entity and skipping if it's @ mention.
                for mention in self.entities:
                    # Catch first text mention
                    if mention.type == "text_mention":
                        user_e = mention.user.id
                        break
            # User @ Mention.
            if user.startswith("@"):
                user_e = user
        return user_e, text

    def _filter(self) -> None:
        if self._filtered:
            return

        prefix = str(self._kwargs.get('prefix', '-'))
        del_pre = bool(self._kwargs.get('del_pre', False))
        input_str = self.input_str
        for i in input_str.strip().split(" "):
            match = re.match(f"({prefix}[a-zA-Z]+)([0-9]*)$", i)
            if match:
                items: Sequence[str] = match.groups()
                self._flags[items[0].lstrip(prefix).lower() if del_pre
                            else items[0].lower()] = items[1] or ''
            else:
                self._filtered_input_str += ' ' + i
        self._filtered_input_str = self._filtered_input_str.strip()
        _LOG.debug(
            _LOG_STR,
            f"Filtered Input String => [ {self._filtered_input_str}, {self._flags} ]")
        self._filtered = True

    @property
    def _key(self) -> str:
        return f"{self.chat.id}.{self.message_id}"

    def _call_cancel_callbacks(self) -> bool:
        callbacks = _CANCEL_CALLBACKS.pop(self._key, None)
        if not callbacks:
            return False
        for callback in callbacks:
            callback()
        return True

    @staticmethod
    def _call_all_cancel_callbacks() -> int:
        i = 0
        for callbacks in _CANCEL_CALLBACKS.values():
            for callback in callbacks:
                callback()
                i += 1
        _CANCEL_CALLBACKS.clear()
        return i

    @contextmanager
    def cancel_callback(self, callback: Optional[Callable[[], Any]] = None) -> None:
        """ run in a cancelable context. callback will be called when user cancel it. """
        is_first = False
        key = self._key
        if key not in _CANCEL_CALLBACKS:
            _CANCEL_CALLBACKS[key] = []
            if not self._process_canceled:
                _CANCEL_CALLBACKS[key].append(
                    lambda: setattr(self, '_process_canceled', True))
            is_first = True
        if callback:
            _CANCEL_CALLBACKS[key].append(callback)
        try:
            yield
        finally:
            try:
                if is_first:
                    del _CANCEL_CALLBACKS[key]
                elif callback:
                    _CANCEL_CALLBACKS[key].remove(callback)
            except (KeyError, ValueError):
                pass

    async def canceled(self, reply=False) -> None:
        """\nedit or reply that process canceled

        Parameters:
            reply (``bool``):
                reply msg if True, else edit
        """
        if reply:
            func = self.reply
        else:
            func = self.edit
        await func("`Process Canceled!`", del_in=5)

    async def send_as_file(self,
                           text: str,
                           filename: str = "output.txt",
                           caption: str = '',
                           log: Union[bool, str] = False,
                           delete_message: bool = True) -> 'Message':
        """\nYou can send large outputs as file

        Example:
                message.send_as_file(text="hello")

        Parameters:
            text (``str``):
                Text of the message to be sent.

            filename (``str``, *optional*):
                file_name for output file.

            caption (``str``, *optional*):
                caption for output file.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            delete_message (``bool``, *optional*):
                If ``True``, the message will be deleted
                after sending the file.

        Returns:
            On success, the sent Message is returned.
        """
        reply_to_id = self.reply_to_message.message_id if self.reply_to_message \
            else self.message_id
        if delete_message:
            asyncio.get_event_loop().create_task(self.delete())
        if log and isinstance(log, bool):
            log = self._module
        return await self._client.send_as_file(chat_id=self.chat.id,
                                               text=text,
                                               filename=filename,
                                               caption=caption,
                                               log=log,
                                               reply_to_message_id=reply_to_id)

    async def reply(self,
                    text: str,
                    del_in: int = -1,
                    log: Union[bool, str] = False,
                    quote: Optional[bool] = None,
                    parse_mode: Union[str, object] = object,
                    disable_web_page_preview: Optional[bool] = None,
                    disable_notification: Optional[bool] = None,
                    reply_to_message_id: Optional[int] = None,
                    reply_markup: InlineKeyboardMarkup = None) -> Union['Message', bool]:
        """\nExample:
                message.reply("hello")

        Parameters:
            text (``str``):
                Text of the message to be sent.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent as
                a reply to this message.
                If *reply_to_message_id* is passed,
                this parameter will be ignored.
                Defaults to ``True`` in group chats
                and ``False`` in private chats.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both
                Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.

            reply_markup (:obj:`InlineKeyboardMarkup`
            | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove`
            | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard,
                custom reply keyboard,
                instructions to remove reply keyboard or to
                force a reply from the user.

        Returns:
            On success, the sent Message or True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if quote is None:
            quote = self.chat.type != "private"
        if reply_to_message_id is None and quote:
            reply_to_message_id = self.message_id
        if log and isinstance(log, bool):
            log = self._module
        return await self._client.send_message(chat_id=self.chat.id,
                                               text=text,
                                               del_in=del_in,
                                               log=log,
                                               parse_mode=parse_mode,
                                               disable_web_page_preview=disable_web_page_preview,
                                               disable_notification=disable_notification,
                                               reply_to_message_id=reply_to_message_id,
                                               reply_markup=reply_markup)

    reply_text = reply

    async def edit(self,
                   text: str,
                   del_in: int = -1,
                   log: Union[bool, str] = False,
                   sudo: bool = True,
                   parse_mode: Union[str, object] = object,
                   disable_web_page_preview: Optional[bool] = None,
                   reply_markup: InlineKeyboardMarkup = None) -> Union['Message', bool]:
        """\nExample:
                message.edit_text("hello")

        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            sudo (``bool``, *optional*):
                If ``True``, sudo users supported.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success, the edited
            :obj:`Message` or True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if log and isinstance(log, bool):
            log = self._module
        try:
            return await self._client.edit_message_text(
                chat_id=self.chat.id,
                message_id=self.message_id,
                text=text,
                del_in=del_in,
                log=log,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup)
        except MessageNotModified:
            return self
        except (MessageAuthorRequired, MessageIdInvalid) as m_er:
            if sudo:
                msg = await self.reply(text=text,
                                       del_in=del_in,
                                       log=log,
                                       parse_mode=parse_mode,
                                       disable_web_page_preview=disable_web_page_preview,
                                       reply_markup=reply_markup)
                if isinstance(msg, Message):
                    self.message_id = msg.message_id  # pylint: disable=W0201
                return msg
            raise m_er

    edit_text = try_to_edit = edit

    async def force_edit(self,
                         text: str,
                         del_in: int = -1,
                         log: Union[bool, str] = False,
                         parse_mode: Union[str, object] = object,
                         disable_web_page_preview: Optional[bool] = None,
                         reply_markup: InlineKeyboardMarkup = None,
                         **kwargs) -> Union['Message', bool]:
        """\nThis will first try to message.edit.
        If it raise MessageAuthorRequired or
        MessageIdInvalid error, run message.reply.

        Example:
                message.force_edit(text='force_edit', del_in=3)

        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both
                Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            **kwargs (for message.reply)

        Returns:
            On success, the edited or replied
            :obj:`Message` or True is returned.
        """
        try:
            return await self.edit(text=text,
                                   del_in=del_in,
                                   log=log,
                                   sudo=False,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview,
                                   reply_markup=reply_markup)
        except (MessageAuthorRequired, MessageIdInvalid):
            return await self.reply(text=text,
                                    del_in=del_in,
                                    log=log,
                                    parse_mode=parse_mode,
                                    disable_web_page_preview=disable_web_page_preview,
                                    reply_markup=reply_markup,
                                    **kwargs)

    async def err(self,
                  text: str,
                  del_in: int = -1,
                  show_help: bool = True,
                  log: Union[bool, str] = False,
                  sudo: bool = True,
                  parse_mode: Union[str, object] = object,
                  disable_web_page_preview: Optional[bool] = None,
                  reply_markup: InlineKeyboardMarkup = None) -> Union['Message', bool]:
        """\nYou can send error messages with command info button using this method

        Example:
                message.err(text='error', del_in=3)
        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            show_help (``bool``):
                Show help if available

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            sudo (``bool``, *optional*):
                If ``True``, sudo users supported.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            On success,
            If Client of message is Userge:
                the sent :obj:`Message` or True is returned.
            if Client of message is UsergeBot:
                the edited :obj:`Message` or True is returned.
        """
        if show_help:
            command_name = self.text.split()[0].strip()
            cmd = command_name.lstrip(Config.CMD_TRIGGER).lstrip(Config.SUDO_TRIGGER)
            is_cmd = is_command(cmd)
        else:
            is_cmd = False
        if not is_cmd or not bool(Config.BOT_TOKEN):
            del_in = del_in if del_in > 0 else _ERROR_MSG_DELETE_TIMEOUT
            return await self.edit(text=_ERROR_STRING.format(text),
                                   del_in=del_in,
                                   log=log,
                                   sudo=sudo,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview,
                                   reply_markup=reply_markup)
        bot_username = (await self._client.get_me()).username
        if self._client.is_bot:
            btn = [InlineKeyboardButton("Info!", url=f"t.me/{bot_username}?start={cmd}")]
            if reply_markup:
                reply_markup.inline_keyboard.append(btn)
            else:
                reply_markup = InlineKeyboardMarkup([btn])
            msg_obj = await self.edit(text=_ERROR_STRING.format(text),
                                      del_in=del_in,
                                      log=log,
                                      sudo=sudo,
                                      parse_mode=parse_mode,
                                      disable_web_page_preview=disable_web_page_preview,
                                      reply_markup=reply_markup)
        else:
            bot_username = (await self._client.bot.get_me()).username
            try:
                k = await self._client.get_inline_bot_results(
                    bot_username, f"msg.err {cmd} {_ERROR_STRING.format(text)}"
                )
                await self.delete()
                msg_obj = await self._client.send_inline_bot_result(
                    self.chat.id, query_id=k.query_id,
                    result_id=k.results[2].id, hide_via=True
                )
            except (IndexError, BotInlineDisabled):
                del_in = del_in if del_in > 0 else _ERROR_MSG_DELETE_TIMEOUT
                msg_obj = await self.edit(text=_ERROR_STRING.format(text),
                                          del_in=del_in,
                                          log=log,
                                          sudo=sudo,
                                          parse_mode=parse_mode,
                                          disable_web_page_preview=disable_web_page_preview,
                                          reply_markup=reply_markup)
        return msg_obj

    async def force_err(self,
                        text: str,
                        del_in: int = -1,
                        show_help: bool = True,
                        log: Union[bool, str] = False,
                        parse_mode: Union[str, object] = object,
                        disable_web_page_preview: Optional[bool] = None,
                        reply_markup: InlineKeyboardMarkup = None,
                        **kwargs) -> Union['Message', bool]:
        """\nThis will first try to message.err.
        If it raise MessageAuthorRequired or
        MessageIdInvalid error, run message.reply.

        Example:
                message.force_err(text='force_err', del_in=3)

        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            show_help (``bool``):
                Show help if available

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            **kwargs (for message.reply)

        Returns:
            On success,
            If Client of message is Userge:
                the sent :obj:`Message` or True is returned.
            if Client of message is UsergeBot:
                the edited or replied :obj:`Message` or True is returned.
        """
        try:
            msg_obj = await self.err(text=text,
                                     del_in=del_in,
                                     show_help=show_help,
                                     log=log,
                                     parse_mode=parse_mode,
                                     disable_web_page_preview=disable_web_page_preview,
                                     reply_markup=reply_markup)
        except (MessageAuthorRequired, MessageIdInvalid):
            if show_help:
                command_name = self.text.split()[0].strip()
                cmd = command_name.lstrip(Config.CMD_TRIGGER).lstrip(Config.SUDO_TRIGGER)
                is_cmd = is_command(cmd)
            else:
                is_cmd = False
            if not is_cmd or not bool(Config.BOT_TOKEN):
                del_in = del_in if del_in > 0 else _ERROR_MSG_DELETE_TIMEOUT
                return await self.reply(text=_ERROR_STRING.format(text),
                                        del_in=del_in,
                                        log=log,
                                        parse_mode=parse_mode,
                                        disable_web_page_preview=disable_web_page_preview,
                                        reply_markup=reply_markup)
            bot_username = (await self._client.get_me()).username
            if self._client.is_bot:
                btn = [InlineKeyboardButton("Info!", url=f"t.me/{bot_username}?start={cmd}")]
                if reply_markup:
                    reply_markup.inline_keyboard.append(btn)
                else:
                    reply_markup = InlineKeyboardMarkup([btn])
                msg_obj = await self.reply(text=_ERROR_STRING.format(text),
                                           del_in=del_in,
                                           log=log,
                                           parse_mode=parse_mode,
                                           disable_web_page_preview=disable_web_page_preview,
                                           reply_markup=reply_markup)
            else:
                bot_username = (await self._client.bot.get_me()).username
                try:
                    k = await self._client.get_inline_bot_results(
                        bot_username, f"msg.err {cmd} {_ERROR_STRING.format(text)}"
                    )
                    await self.delete()
                    msg_obj = await self._client.send_inline_bot_result(
                        self.chat.id, query_id=k.query_id,
                        result_id=k.results[2].id, hide_via=True
                    )
                except (IndexError, BotInlineDisabled):
                    del_in = del_in if del_in > 0 else _ERROR_MSG_DELETE_TIMEOUT
                    msg_obj = await self.reply(text=_ERROR_STRING.format(text),
                                               del_in=del_in,
                                               log=log,
                                               parse_mode=parse_mode,
                                               disable_web_page_preview=disable_web_page_preview,
                                               reply_markup=reply_markup)
        return msg_obj

    async def edit_or_send_as_file(self,
                                   text: str,
                                   del_in: int = -1,
                                   log: Union[bool, str] = False,
                                   sudo: bool = True,
                                   parse_mode: Union[str, object] = object,
                                   disable_web_page_preview: Optional[bool] = None,
                                   reply_markup: InlineKeyboardMarkup = None,
                                   **kwargs) -> Union['Message', bool]:
        """\nThis will first try to message.edit.
        If it raise MessageTooLong error,
        run message.send_as_file.

        Example:
                message.edit_or_send_as_file("some huge text")

        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            sudo (``bool``, *optional*):
                If ``True``, sudo users supported.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using both
                Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            **kwargs (for message.send_as_file)

        Returns:
            On success, the edited
            :obj:`Message` or True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        try:
            return await self.edit(text=text,
                                   del_in=del_in,
                                   log=log,
                                   sudo=sudo,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview,
                                   reply_markup=reply_markup)
        except (MessageTooLong, OSError):
            return await self.send_as_file(text=text, log=log, **kwargs)

    async def reply_or_send_as_file(self,
                                    text: str,
                                    del_in: int = -1,
                                    log: Union[bool, str] = False,
                                    quote: Optional[bool] = None,
                                    parse_mode: Union[str, object] = object,
                                    disable_web_page_preview: Optional[bool] = None,
                                    disable_notification: Optional[bool] = None,
                                    reply_to_message_id: Optional[int] = None,
                                    reply_markup: InlineKeyboardMarkup = None,
                                    **kwargs) -> Union['Message', bool]:
        """\nThis will first try to message.reply.
        If it raise MessageTooLong error,
        run message.send_as_file.

        Example:
                message.reply_or_send_as_file("some huge text")

        Parameters:
            text (``str``):
                Text of the message to be sent.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be forwarded
                to the log channel.
                If ``str``, the logger name will be updated.

            quote (``bool``, *optional*):
                If ``True``, the message will be sent
                as a reply to this message.
                If *reply_to_message_id* is passed,
                this parameter will be ignored.
                Defaults to ``True`` in group chats
                and ``False`` in private chats.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the
                original message.

            reply_markup (:obj:`InlineKeyboardMarkup`
            | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove`
            | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an
                inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard
                or to force a reply from the user.

            **kwargs (for message.send_as_file)

        Returns:
            On success, the sent Message or True is returned.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        try:
            return await self.reply(text=text,
                                    del_in=del_in,
                                    log=log,
                                    quote=quote,
                                    parse_mode=parse_mode,
                                    disable_web_page_preview=disable_web_page_preview,
                                    disable_notification=disable_notification,
                                    reply_to_message_id=reply_to_message_id,
                                    reply_markup=reply_markup)
        except MessageTooLong:
            return await self.send_as_file(text=text, log=log, **kwargs)

    async def force_edit_or_send_as_file(self,
                                         text: str,
                                         del_in: int = -1,
                                         log: Union[bool, str] = False,
                                         parse_mode: Union[str, object] = object,
                                         disable_web_page_preview: Optional[bool] = None,
                                         reply_markup: InlineKeyboardMarkup = None,
                                         **kwargs) -> Union['Message', bool]:
        """\nThis will first try to message.edit_or_send_as_file.
        If it raise MessageAuthorRequired
        or MessageIdInvalid error, run message.reply_or_send_as_file.

        Example:
                message.force_edit_or_send_as_file("some huge text")

        Parameters:
            text (``str``):
                New text of the message.

            del_in (``int``):
                Time in Seconds for delete that message.

            log (``bool`` | ``str``, *optional*):
                If ``True``, the message will be
                forwarded to the log channel.
                If ``str``, the logger name will be updated.

            parse_mode (``str``, *optional*):
                By default, texts are parsed using
                both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable
                Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.

            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.

            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            **kwargs (for message.reply and message.send_as_file)

        Returns:
            On success, the edited or replied
            :obj:`Message` or True is returned.
        """
        try:
            return await self.edit_or_send_as_file(
                text=text,
                del_in=del_in,
                log=log,
                sudo=False,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup,
                **kwargs)
        except (MessageAuthorRequired, MessageIdInvalid):
            return await self.reply_or_send_as_file(
                text=text,
                del_in=del_in,
                log=log,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup,
                **kwargs)

    # pylint: disable=arguments-differ
    async def delete(self, revoke: bool = True, sudo: bool = True) -> bool:
        """\nThis will first try to delete and ignore
        it if it raises MessageDeleteForbidden

        Parameters:
            revoke (``bool``, *optional*):
                Deletes messages on both parts.
                This is only for private cloud chats and normal groups, messages on
                channels and supergroups are always revoked (i.e.: deleted for everyone).
                Defaults to True.

            sudo (``bool``, *optional*):
                If ``True``, sudo users supported.

        Returns:
            True on success, False otherwise.
        """
        try:
            return bool(await super().delete(revoke=revoke))
        except MessageDeleteForbidden as m_e:
            if not sudo:
                raise m_e
            return False
