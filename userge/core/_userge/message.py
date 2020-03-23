import re
import os
import asyncio
from typing import Dict, Union, List
from .base import Base
from pyrogram import (
    Client, Message as Msg,
    InlineKeyboardMarkup)


class Message(Base, Msg):

    __ERROR_MSG_DELETE_TIMEOUT = 3
    __ERROR_STRING = "**ERROR**: `{}`"

    def __init__(self,
                 message: Msg,
                 client: Client,
                 **kwargs):

        self._client = client
        self.message_id = message.message_id
        self.date = message.date
        self.chat = message.chat
        self.from_user = message.from_user
        self.forward_from = message.forward_from
        self.forward_sender_name = message.forward_sender_name
        self.forward_from_chat = message.forward_from_chat
        self.forward_from_message_id = message.forward_from_message_id
        self.forward_signature = message.forward_signature
        self.forward_date = message.forward_date
        self.reply_to_message = message.reply_to_message
        self.mentioned = message.mentioned
        self.empty = message.empty
        self.service = message.service
        self.scheduled = message.scheduled
        self.from_scheduled = message.from_scheduled
        self.media = message.media
        self.edit_date = message.edit_date
        self.media_group_id = message.media_group_id
        self.author_signature = message.author_signature
        self.text = message.text
        self.entities = message.entities
        self.caption_entities = message.caption_entities
        self.audio = message.audio
        self.document = message.document
        self.photo = message.photo
        self.sticker = message.sticker
        self.animation = message.animation
        self.game = message.game
        self.video = message.video
        self.voice = message.voice
        self.video_note = message.video_note
        self.caption = message.caption
        self.contact = message.contact
        self.location = message.location
        self.venue = message.venue
        self.web_page = message.web_page
        self.poll = message.poll
        self.new_chat_members = message.new_chat_members
        self.left_chat_member = message.left_chat_member
        self.new_chat_title = message.new_chat_title
        self.new_chat_photo = message.new_chat_photo
        self.delete_chat_photo = message.delete_chat_photo
        self.group_chat_created = message.group_chat_created
        self.supergroup_chat_created = message.supergroup_chat_created
        self.channel_chat_created = message.channel_chat_created
        self.migrate_to_chat_id = message.migrate_to_chat_id
        self.migrate_from_chat_id = message.migrate_from_chat_id
        self.pinned_message = message.pinned_message
        self.game_high_score = message.game_high_score
        self.views = message.views
        self.via_bot = message.via_bot
        self.outgoing = message.outgoing
        self.matches = message.matches
        self.command = message.command
        self.reply_markup = message.reply_markup
        self.__filtered_input_str: str = None
        self.__flags: Dict[str, str] = None
        self.__kwargs = kwargs
        del message

    @property
    def input_str(self) -> str:
        input_ = self.text

        if ' ' in input_:
            return input_.split(maxsplit=1)[1].strip()

        else:
            return ''

    @property
    def filtered_input_str(self) -> str:
        self.__filter()

        return self.__filtered_input_str

    @property
    def flags(self) -> Dict[str, str]:
        self.__filter()

        return self.__flags

    def __filter(self) -> None:

        if self.__filtered_input_str is None or self.__flags is None:
            prefix: str = self.__kwargs.get('prefix', '-')
            del_pre: bool = self.__kwargs.get('del_pre', False)
            input_str: str = self.matches[0].group(1) or ''

            text: List[str] = []
            flags: Dict[str, Union[str, bool, int]] = {}

            for i in input_str.strip().split():
                match = re.match(f"({prefix}[a-z]+)($|[0-9]+)?$", i)

                if match:
                    items: List[Union[str, None]] = match.groups()
                    flags[items[0].lstrip(prefix) if del_pre \
                        else items[0]] = items[1] or ''

                else:
                    text.append(i)

            text = ' '.join(text)

            self._LOG.info(
                self._SUB_STRING.format(
                    f"Filtered Input String => [ {text}, {flags} ]"))

            self.__filtered_input_str, self.__flags = text, flags

    async def send_as_file(self,
                           text: str,
                           filename: str = "output.txt",
                           caption: str = '',
                           delete_message: bool = True) -> None:

        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(text)

        reply_to_id = self.reply_to_message.message_id if self.reply_to_message \
            else self.message_id

        self._LOG.info(
            self._SUB_STRING.format(f"Uploading {filename} To Telegram"))

        await self._client.send_document(chat_id=self.chat.id,
                                          document=filename,
                                          caption=caption,
                                          disable_notification=True,
                                          reply_to_message_id=reply_to_id)

        os.remove(filename)

        if delete_message:
            await self.delete()

    async def reply(self,
                    text: str,
                    del_in: int = -1,
                    quote: bool = None,
                    parse_mode: Union[str, None] = object,
                    disable_web_page_preview: bool = None,
                    disable_notification: bool = None,
                    reply_to_message_id: int = None,
                    reply_markup: InlineKeyboardMarkup = None,
                    **kwargs) -> Msg:

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
            msg = await msg.delete()

        return msg

    async def edit(self,
                   text: str,
                   del_in: int = -1,
                   parse_mode: Union[str, None] = object,
                   disable_web_page_preview: bool = None,
                   reply_markup: InlineKeyboardMarkup = None,
                   **kwargs) -> Msg:

        msg =  await self._client.edit_message_text(chat_id=self.chat.id,
                                                    message_id=self.message_id,
                                                    text=text,
                                                    parse_mode=parse_mode,
                                                    disable_web_page_preview=disable_web_page_preview,
                                                    reply_markup=reply_markup)

        if del_in > 0:
            await asyncio.sleep(del_in)
            msg = await msg.delete()

        return msg

    async def force_edit(self,
                         text: str,
                         del_in: int = -1,
                         parse_mode: Union[str, None] = object,
                         disable_web_page_preview: bool = None,
                         reply_markup: InlineKeyboardMarkup = None,
                         **kwargs) -> None:
        try:
            await self.edit(text=text,
                            del_in=del_in,
                            parse_mode=parse_mode,
                            disable_web_page_preview=disable_web_page_preview,
                            reply_markup=reply_markup,
                            **kwargs)

        except:
            msg = await self.reply(text=text,
                                   del_in=del_in,
                                   parse_mode=parse_mode,
                                   disable_web_page_preview=disable_web_page_preview,
                                   reply_markup=reply_markup,
                                   **kwargs)

        else:
            msg = self

        if del_in > 0:
            await asyncio.sleep(del_in)
            try:
                await msg.delete()
            except:
                pass

    async def err(self,
                  text: str,
                  del_in: int = -1,
                  parse_mode: Union[str, None] = object,
                  disable_web_page_preview: bool = None,
                  reply_markup: InlineKeyboardMarkup = None,
                  **kwargs) -> None:
        
        del_in = del_in if del_in > 0 \
            else self.__ERROR_MSG_DELETE_TIMEOUT

        await self.edit(text=self.__ERROR_STRING.format(text),
                        del_in=del_in,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview,
                        reply_markup=reply_markup,
                        **kwargs)

    async def force_err(self,
                        text: str,
                        del_in: int = -1,
                        parse_mode: Union[str, None] = object,
                        disable_web_page_preview: bool = None,
                        reply_markup: InlineKeyboardMarkup = None,
                        **kwargs) -> None:

        del_in = del_in if del_in > 0 \
            else self.__ERROR_MSG_DELETE_TIMEOUT

        await self.force_edit(text=self.__ERROR_STRING.format(text),
                              del_in=del_in,
                              parse_mode=parse_mode,
                              disable_web_page_preview=disable_web_page_preview,
                              reply_markup=reply_markup,
                              **kwargs)
