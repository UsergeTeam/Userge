import re
import os
import asyncio
from typing import Dict, Union, Optional, Sequence

from pyrogram import Client, Message as Msg, InlineKeyboardMarkup
from pyrogram.errors.exceptions import MessageAuthorRequired
from .base import Base


class Message(Msg, Base):
    """
    Moded Message Class For Userge
    """

    __ERROR_MSG_DELETE_TIMEOUT = 5
    __ERROR_STRING = "**ERROR**: `{}`"

    def __init__(self,
                 client: Client,
                 message: Msg,
                 **kwargs) -> None:

        super().__init__(client=client,
                         **self._msg_to_dict(message))

        self.__filtered = False
        self.__filtered_input_str: str = ''
        self.__flags: Dict[str, str] = {}
        self.__kwargs = kwargs

    @property
    def input_str(self) -> str:
        """
        Returns the input string without command.
        """

        input_ = self.text

        if ' ' in input_:
            return str(input_.split(maxsplit=1)[1].strip())

        else:
            return ''

    @property
    def filtered_input_str(self) -> str:
        """
        Returns the filtered input string without command and flags.
        """

        self.__filter()

        return self.__filtered_input_str

    @property
    def flags(self) -> Dict[str, str]:
        """
        Returns all flags in input string as `Dict`.
        """

        self.__filter()

        return self.__flags

    def __filter(self) -> None:

        if not self.__filtered:
            prefix: str = self.__kwargs.get('prefix', '-')
            del_pre: bool = self.__kwargs.get('del_pre', False)
            input_str: str = self.input_str

            for i in input_str.strip().split():
                match = re.match(f"({prefix}[a-z]+)($|[0-9]+)?$", i)

                if match:
                    items: Sequence[str] = match.groups()
                    self.__flags[items[0].lstrip(prefix) if del_pre \
                        else items[0]] = items[1] or ''

                else:
                    self.__filtered_input_str += ' ' + i

            self.__filtered_input_str = self.__filtered_input_str.strip()

            self._LOG.info(
                self._SUB_STRING.format(
                    f"Filtered Input String => [ {self.__filtered_input_str}, {self.__flags} ]"))

            self.__filtered = True

    async def send_as_file(self,
                           text: str,
                           filename: str = "output.txt",
                           caption: str = '',
                           delete_message: bool = True) -> Msg:
        """
        You can send large outputs as file

        Example:
                message.send_as_file(text="hello")

        Parameters:
            text (``str``):
                Text of the message to be sent.
            filename (``str``, *optional*):
                file_name for output file.
            caption (``str``, *optional*):
                caption for output file.
            delete_message (``bool``, *optional*):
                If ``True``, the message will be deleted after sending the file.
        Returns:
            On success, the sent Message is returned.
        """

        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(text)

        reply_to_id = self.reply_to_message.message_id if self.reply_to_message \
            else self.message_id

        self._LOG.info(
            self._SUB_STRING.format(f"Uploading {filename} To Telegram"))

        msg = await self._client.send_document(chat_id=self.chat.id,
                                               document=filename,
                                               caption=caption,
                                               disable_notification=True,
                                               reply_to_message_id=reply_to_id)

        os.remove(filename)

        if delete_message:
            await self.delete()

        return Message(self._client, msg)

    async def reply(self,
                    text: str,
                    del_in: int = -1,
                    quote: Optional[bool] = None,
                    parse_mode: Union[str, object] = object,
                    disable_web_page_preview: Optional[bool] = None,
                    disable_notification: Optional[bool] = None,
                    reply_to_message_id: Optional[int] = None,
                    reply_markup: InlineKeyboardMarkup = None) -> Msg:
        """
        Example:
                message.reply("hello")

        Parameters:
            text (``str``):
                Text of the message to be sent.
            del_in (``int``):
                Time in Seconds for delete that message.
            quote (``bool``, *optional*):
                If ``True``, the message will be sent as a reply to this message.
                If *reply_to_message_id* is passed, this parameter will be ignored.
                Defaults to ``True`` in group chats and ``False`` in private chats.
            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.
            reply_to_message_id (``int``, *optional*):
                If the message is a reply, ID of the original message.
            reply_markup (:obj:`InlineKeyboardMarkup` | :obj:`ReplyKeyboardMarkup` | :obj:`ReplyKeyboardRemove` | :obj:`ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
        Returns:
            On success, the sent Message is returned.
        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        if quote is None:
            quote = self.chat.type != "private"

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.message_id

        msg = await self._client.send_message(chat_id=self.chat.id,
                                              text=text,
                                              parse_mode=parse_mode,
                                              disable_web_page_preview=disable_web_page_preview,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_to_message_id,
                                              reply_markup=reply_markup)

        if del_in > 0:
            await asyncio.sleep(del_in)
            await msg.delete()

        return Message(self._client, msg)

    reply_text = reply

    async def edit(self,
                   text: str,
                   del_in: int = -1,
                   parse_mode: Union[str, object] = object,
                   disable_web_page_preview: Optional[bool] = None,
                   reply_markup: InlineKeyboardMarkup = None) -> Msg:
        """
        Example:
                message.edit_text("hello")

        Parameters:
            text (``str``):
                New text of the message.
            del_in (``int``):
                Time in Seconds for delete that message.
            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.
        Returns:
            On success, the edited :obj:`Message` is returned.
        Raises:
            RPCError: In case of a Telegram RPC error.
        """

        msg = await self._client.edit_message_text(chat_id=self.chat.id,
                                                   message_id=self.message_id,
                                                   text=text,
                                                   parse_mode=parse_mode,
                                                   disable_web_page_preview=disable_web_page_preview,
                                                   reply_markup=reply_markup)

        if del_in > 0:
            await asyncio.sleep(del_in)
            await msg.delete()

        return Message(self._client, msg)

    edit_text = edit

    async def force_edit(self,
                         text: str,
                         del_in: int = -1,
                         parse_mode: Union[str, object] = object,
                         disable_web_page_preview: Optional[bool] = None,
                         reply_markup: InlineKeyboardMarkup = None,
                         **kwargs) -> Msg:
        """
        This will first try to edit that message. If it found any errors
        it will reply that message.

        Example:
                message.force_edit(text='force_edit', del_in=3)

        Parameters:
            text (``str``):
                New text of the message.
            del_in (``int``):
                Time in Seconds for delete that message.
            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.
            **kwargs (for reply message)
        Returns:
            On success, the edited or replied :obj:`Message` is returned.
        """

        try:
            msg = await self.edit(text=text,
                                  del_in=del_in,
                                  parse_mode=parse_mode,
                                  disable_web_page_preview=disable_web_page_preview,
                                  reply_markup=reply_markup)

        except MessageAuthorRequired:
            msg = await self.reply(text=text,
                                   del_in=del_in,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview,
                                   reply_markup=reply_markup,
                                   **kwargs)

        if del_in > 0:
            await asyncio.sleep(del_in)
            await msg.delete()

        return Message(self._client, msg)

    async def err(self,
                  text: str,
                  del_in: int = -1,
                  parse_mode: Union[str, object] = object,
                  disable_web_page_preview: Optional[bool] = None,
                  reply_markup: InlineKeyboardMarkup = None) -> Msg:
        """
        You can send error messages using this method

        Example:
                message.err(text='error', del_in=3)

        Parameters:
            text (``str``):
                New text of the message.
            del_in (``int``):
                Time in Seconds for delete that message.
            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.
        Returns:
            On success, the edited :obj:`Message` is returned.
        """

        del_in = del_in if del_in > 0 \
            else self.__ERROR_MSG_DELETE_TIMEOUT

        return await self.edit(text=self.__ERROR_STRING.format(text),
                               del_in=del_in,
                               parse_mode=parse_mode,
                               disable_web_page_preview=disable_web_page_preview,
                               reply_markup=reply_markup)

    async def force_err(self,
                        text: str,
                        del_in: int = -1,
                        parse_mode: Union[str, object] = object,
                        disable_web_page_preview: Optional[bool] = None,
                        reply_markup: InlineKeyboardMarkup = None,
                        **kwargs) -> Msg:
        """
        This will first try to edit that message. If it found any errors
        it will reply that message.

        Example:
                message.force_err(text='force_err', del_in=3)

        Parameters:
            text (``str``):
                New text of the message.
            del_in (``int``):
                Time in Seconds for delete that message.
            parse_mode (``str``, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.
                Pass "markdown" or "md" to enable Markdown-style parsing only.
                Pass "html" to enable HTML-style parsing only.
                Pass None to completely disable style parsing.
            disable_web_page_preview (``bool``, *optional*):
                Disables link previews for links in this message.
            reply_markup (:obj:`InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.
            **kwargs (for reply message)
        Returns:
            On success, the edited or replied :obj:`Message` is returned.
        """

        del_in = del_in if del_in > 0 \
            else self.__ERROR_MSG_DELETE_TIMEOUT

        return await self.force_edit(text=self.__ERROR_STRING.format(text),
                                     del_in=del_in,
                                     parse_mode=parse_mode,
                                     disable_web_page_preview=disable_web_page_preview,
                                     reply_markup=reply_markup,
                                     **kwargs)
