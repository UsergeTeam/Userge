# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

from math import ceil
from typing import List, Callable, Dict, Union, Any
from uuid import uuid4

from pyrogram import filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified, MessageIdInvalid
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InlineQuery)

from userge import userge, Message, config, get_collection
from userge.utils import is_command

_CATEGORY = {
    'admin': '👨‍✈️',
    'fun': '🎨',
    'builtin': '⚙️',
    'tools': '🧰',
    'utils': '🗂',
    'misc': '💎'
}
SAVED_SETTINGS = get_collection("CONFIGS")


@userge.on_start
async def _init() -> None:
    data = await SAVED_SETTINGS.find_one({'_id': 'CURRENT_CLIENT'})
    if data:
        config.Dynamic.USE_USER_FOR_CLIENT_CHECKS = bool(data['is_user'])


@userge.on_cmd("help", about={
    'header': "Guide to use USERGE commands",
    'flags': {'-i': "open help menu in inline"},
    'usage': "{tr}help [flag] [plugin_name | command_name]",
    'examples': [
        "{tr}help", "{tr}help -i", "{tr}help help",
        "{tr}help core", "{tr}help loader"]}, allow_channels=False)
async def helpme(message: Message) -> None:  # pylint: disable=missing-function-docstring
    plugins = userge.manager.loaded_plugins

    if userge.has_bot and '-i' in message.flags:
        bot = (await userge.bot.get_me()).username
        menu = await userge.get_inline_bot_results(bot)
        await userge.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=menu.query_id,
            result_id=menu.results[1].id)
        return await message.delete()

    if not message.input_str:
        out_str = f"""({len(plugins)}) Plugins\n\n"""
        cat_plugins = userge.manager.get_plugins()

        for cat in sorted(cat_plugins):
            out_str += (f"{_CATEGORY.get(cat, '📁')} {cat} ({len(cat_plugins[cat])}):  <code>"
                        + "</code>  <code>".join(sorted(cat_plugins[cat])) + "</code>\n\n")
    else:
        key = message.input_str

        if (not key.startswith(config.CMD_TRIGGER)
                and key in plugins
                and plugins[key].loaded_commands
                and (len(plugins[key].loaded_commands) > 1
                     or plugins[key].loaded_commands[0].name.lstrip(config.CMD_TRIGGER) != key)):
            commands = plugins[key].loaded_commands
            size = len(commands)

            out_str = f"""<b>plugin</b>: <code>{key}</code>
<b>category</b>: <i>{plugins[key].cat}</i>
<b>doc</b>: <i>{plugins[key].doc}</i>

({size}) <b>Command{'s' if size > 1 else ''}</b>\n\n"""

            for cmd in commands:
                out_str += f"<code>{cmd.name}</code>: <i>{cmd.doc}</i>\n"

        else:
            triggers = (
                config.CMD_TRIGGER,
                config.SUDO_TRIGGER,
                config.PUBLIC_TRIGGER)

            for _ in triggers:
                key = key.lstrip(_)

            out_str = f"<i>No Plugin or Command found for</i>: <code>{message.input_str}</code>"

            for name, cmd in userge.manager.loaded_commands.items():
                for _ in triggers:
                    name = name.lstrip(_)

                if key == name:
                    out_str = f"""<b>command</b>: <code>{cmd.name}</code>
<b>plugin</b>: <code>{cmd.plugin}</code>
<b>category</b>: <i>{plugins[cmd.plugin].cat}</i>

{cmd.about}"""
                    break

    await message.edit(out_str,
                       del_in=0,
                       parse_mode=enums.ParseMode.HTML,
                       disable_web_page_preview=True)


if userge.has_bot:

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and c_q.from_user.id in config.OWNER_ID:
                try:
                    await func(c_q)
                except MessageNotModified:
                    await c_q.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)
                except MessageIdInvalid:
                    await c_q.answer("Sorry, I Don't Have Permissions to edit this 😔",
                                     show_alert=True)
            else:
                user_dict = await userge.bot.get_user_dict(config.OWNER_ID[0])
                await c_q.answer(
                    f"Only {user_dict['flname']} Can Access this...! Build Your Own @TheUserge 🤘",
                    show_alert=True)

        return wrapper

    @userge.bot.on_message(filters.private & filters.user(
        list(config.OWNER_ID)) & filters.command("start"), group=-1)
    async def pm_help_handler(_, msg: Message):
        cmd = msg.command[1] if len(msg.command) > 1 else ''

        if not cmd:
            return

        commands = userge.manager.loaded_commands
        key = config.CMD_TRIGGER + cmd
        key_ = config.SUDO_TRIGGER + cmd

        if cmd in commands:
            out_str = f"<code>{cmd}</code>\n\n{commands[cmd].about}"
        elif key in commands:
            out_str = f"<code>{key}</code>\n\n{commands[key].about}"
        elif key_ in commands:
            out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
        else:
            out_str = f"<i>No Command Found for</i>: <code>{cmd}</code>"

        await msg.reply(out_str, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)

    @userge.bot.on_callback_query(
        filters=filters.regex(
            pattern=r"\((.+)\)(next|prev)\((\d+)\)"))
    @check_owner
    async def callback_next_prev(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        n_or_p = str(callback_query.matches[0].group(2))
        p_num = int(callback_query.matches[0].group(3))

        p_num = p_num + 1 if n_or_p == "next" else p_num - 1
        pos_list = cur_pos.split('|')

        if len(pos_list) == 1:
            buttons = parse_buttons(p_num, cur_pos,
                                    lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                                    userge.manager.get_all_plugins())
        elif len(pos_list) == 2:
            buttons = parse_buttons(p_num, cur_pos,
                                    lambda x: f"🗃 {x}",
                                    userge.manager.get_all_plugins()[pos_list[-1]])
        elif len(pos_list) == 3:
            _, buttons = plugin_data(cur_pos, p_num)

        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(buttons))

    @userge.bot.on_callback_query(
        filters=filters.regex(
            pattern=r"back\((.+)\)"))
    @check_owner
    async def callback_back(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')

        if len(pos_list) == 1:
            await callback_query.answer("you are in main menu", show_alert=True)
            return

        if len(pos_list) == 2:
            text = "🖥 **Userge Main Menu** 🖥"
            buttons = main_menu_buttons()
        elif len(pos_list) == 3:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = plugin_data(cur_pos)

        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @userge.bot.on_callback_query(
        filters=filters.regex(
            pattern=r"enter\((.+)\)"))
    @check_owner
    async def callback_enter(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')

        if len(pos_list) == 2:
            text, buttons = category_data(cur_pos)
        elif len(pos_list) == 3:
            text, buttons = plugin_data(cur_pos)
        elif len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)

        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @userge.bot.on_callback_query(
        filters=filters.regex(pattern=r"((?:un)?load)\((.+)\)"))
    @check_owner
    async def callback_manage(callback_query: CallbackQuery):
        task = str(callback_query.matches[0].group(1))
        cur_pos = str(callback_query.matches[0].group(2))
        pos_list = cur_pos.split('|')

        if len(pos_list) == 4:
            if is_filter(pos_list[-1]):
                flt = userge.manager.filters[pos_list[-1]]
            else:
                flt = userge.manager.commands[pos_list[-1]]

            getattr(flt, task)()
            text, buttons = filter_data(cur_pos)

        else:
            plg = userge.manager.plugins[pos_list[-1]]
            await getattr(plg, task)()
            text, buttons = plugin_data(cur_pos)

        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    @userge.bot.on_callback_query(filters=filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):
        await callback_query.edit_message_text(
            "🖥 **Userge Main Menu** 🖥", reply_markup=InlineKeyboardMarkup(main_menu_buttons()))

    @userge.bot.on_callback_query(filters=filters.regex(pattern=r"^chgclnt$"))
    @check_owner
    async def callback_chgclnt(callback_query: CallbackQuery):
        if not userge.dual_mode:
            return await callback_query.answer(
                "you using [BOT MODE], can't change client.", show_alert=True)

        config.Dynamic.USER_IS_PREFERRED = not config.Dynamic.USER_IS_PREFERRED

        await SAVED_SETTINGS.update_one({'_id': 'CURRENT_CLIENT'},
                                        {"$set": {
                                            'is_user': config.Dynamic.USER_IS_PREFERRED}},
                                        upsert=True)

        await callback_query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(main_menu_buttons()))

    @userge.bot.on_callback_query(
        filters=filters.regex(
            pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')

        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)
        await callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(buttons))

    def is_filter(name: str) -> bool:
        split_ = name.split('.')

        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(page_num: int,
                      cur_pos: str,
                      func: Callable[[str], str],
                      data: Union[List[str], Dict[str, Any]],
                      rows: int = 3):
        buttons = [
            InlineKeyboardButton(
                func(x),
                callback_data=f"enter({cur_pos}|{x})".encode()) for x in sorted(data)]

        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))

        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])

        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages

        if len(pairs) > rows:
            pairs = pairs[current_page * rows:(current_page + 1) * rows] + [
                [
                    InlineKeyboardButton(
                        "⏪ Previous", callback_data=f"({cur_pos})prev({current_page})".encode()),
                    InlineKeyboardButton(
                        "⏩ Next", callback_data=f"({cur_pos})next({current_page})".encode())],
            ]

        pairs += default_buttons(cur_pos)

        return pairs

    def main_menu_buttons():
        return parse_buttons(0, "mm",
                             lambda x: f"{_CATEGORY.get(x, '📁')} {x}",
                             userge.manager.get_all_plugins())

    def default_buttons(cur_pos: str):
        tmp_btns = []

        if cur_pos != "mm":
            tmp_btns.append(InlineKeyboardButton(
                "⬅ Back", callback_data=f"back({cur_pos})".encode()))

            if len(cur_pos.split('|')) > 2:
                tmp_btns.append(InlineKeyboardButton(
                    "🖥 Main Menu", callback_data="mm".encode()))
                tmp_btns.append(InlineKeyboardButton(
                    "🔄 Refresh", callback_data=f"refresh({cur_pos})".encode()))

        elif userge.dual_mode:
            cur_clnt = "👲 USER" if config.Dynamic.USER_IS_PREFERRED else "🤖 BOT"
            tmp_btns.append(
                InlineKeyboardButton(
                    f"🔩 Preferred Client : {cur_clnt}",
                    callback_data="chgclnt".encode()))

        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plugins = userge.manager.get_all_plugins()[pos_list[1]]

        text = (
            f"**(`{len(plugins)}`) Plugin(s) Under : "
            f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}` 🎭 Category**")

        buttons = parse_buttons(0, '|'.join(pos_list[:2]),
                                lambda x: f"🗃 {x}",
                                plugins)

        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):

        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]

        text = f"""🗃 **--Plugin Status--** 🗃

🔖 **Name** : `{plg.name}`
🎭 **Category** : `{pos_list[1]}`
📝 **Doc** : `{plg.doc}`
⚔ **Commands** : `{len(plg.commands)}`
⚖ **Filters** : `{len(plg.filters)}`
✅ **Loaded** : `{plg.loaded}`
"""
        tmp_btns = []

        if plg.loaded:
            tmp_btns.append(
                InlineKeyboardButton(
                    "❎ Unload",
                    callback_data=f"unload({'|'.join(pos_list[:3])})".encode()))
        else:
            tmp_btns.append(
                InlineKeyboardButton(
                    "✅ Load",
                    callback_data=f"load({'|'.join(pos_list[:3])})".encode()))

        buttons = parse_buttons(p_num,
                                '|'.join(pos_list[:3]),
                                lambda x: f"⚖ {x}" if is_filter(x) else f"⚔ {x}",
                                (flt.name for flt in plg.commands + plg.filters))

        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]

        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]

        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]

        flt_data = f"""
🔖 **Name** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.loaded}`"""

        if hasattr(flt, 'about'):
            text = f"""⚔ **--Command Status--**
{flt_data}

{flt.about}
"""
        else:
            text = f"""⚖ **--Filter Status--** ⚖
{flt_data}
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []

        if flt.loaded:
            tmp_btns.append(InlineKeyboardButton(
                "❎ Unload", callback_data=f"unload({cur_pos})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "✅ Load", callback_data=f"load({cur_pos})".encode()))

        buttons = [tmp_btns] + buttons

        return text, buttons

    @userge.bot.on_inline_query(group=1)
    async def inline_answer(_, inline_query: InlineQuery):
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Repo",
                input_message_content=InputTextMessageContent(
                    "**Here's how to setup Userge** 😎"
                ),
                url="https://github.com/UsergeTeam/Userge",
                description="Setup Your Own",
                thumb_url="https://imgur.com/download/Inyeb1S",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🧰 Userge Repo",
                                url="https://github.com/UsergeTeam/Userge"),
                            InlineKeyboardButton(
                                "🖥 Deploy Userge",
                                url="https://t.me/theUserge/102")
                        ]
                    ]
                )
            )
        ]

        if inline_query.from_user and inline_query.from_user.id in config.OWNER_ID:
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Main Menu",
                    input_message_content=InputTextMessageContent(
                        "🖥 **Userge Main Menu** 🖥"
                    ),
                    url="https://github.com/UsergeTeam/Userge",
                    description="Userge Main Menu",
                    thumb_url="https://imgur.com/download/Inyeb1S",
                    reply_markup=InlineKeyboardMarkup(main_menu_buttons())
                )
            )

            if "msg.err" in inline_query.query:
                if ' ' not in inline_query.query:
                    return

                tmp = inline_query.query.split(' ', maxsplit=2)

                if len(tmp) != 3:
                    return

                _, cmd, err_text = tmp

                if cmd and err_text and is_command(cmd):
                    bot_username = (await userge.bot.get_me()).username

                    button = [
                        [
                            InlineKeyboardButton(
                                "Info!", url=f"t.me/{bot_username}?start={cmd}"
                            )
                        ]
                    ]

                    results.append(
                        InlineQueryResultArticle(
                            id=uuid4(),
                            title="Inline Error Text",
                            input_message_content=InputTextMessageContent(err_text),
                            description="Inline Error text with help support button.",
                            thumb_url="https://imgur.com/download/Inyeb1S",
                            reply_markup=InlineKeyboardMarkup(button)))

        await inline_query.answer(results=results, cache_time=3)
