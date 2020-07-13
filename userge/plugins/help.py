# pylint: disable=missing-module-docstring
#
# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

from math import ceil
from uuid import uuid4
from typing import List, Callable, Dict, Union, Any

from pyrogram import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Filters, CallbackQuery, InlineQuery)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

from userge import userge, Message, Config

_CATEGORY = {
    'admin': '👨‍✈️',
    'fun': '🎨',
    'misc': '⚙️',
    'tools': '🧰',
    'utils': '🗂',
    'unofficial': '🃏',
    'temp': '♻️',
    'plugins': '💎'
}


@userge.on_cmd("help", about={'header': "Guide to use USERGE commands"}, allow_channels=False)
async def helpme(message: Message) -> None:  # pylint: disable=missing-function-docstring
    plugins = userge.manager.enabled_plugins
    if not message.input_str:
        out_str = f"""⚒ <b><u>(<code>{len(plugins)}</code>) Plugins Available</u></b>\n\n"""
        cat_plugins = userge.manager.get_all_plugins()
        for cat in sorted(cat_plugins):
            out_str += (f"    {_CATEGORY.get(cat, '📁')} <b>{cat}</b> "
                        f"(<code>{len(cat_plugins[cat])}</code>) :   <code>"
                        + "</code>    <code>".join(sorted(cat_plugins[cat])) + "</code>\n\n")
        out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [plugin_name]</code>"""
    else:
        key = message.input_str
        if (not key.startswith(Config.CMD_TRIGGER)
                and key in plugins
                and (len(plugins[key].enabled_commands) > 1
                     or plugins[key].enabled_commands[0].name.lstrip(Config.CMD_TRIGGER) != key)):
            commands = plugins[key].enabled_commands
            out_str = f"""⚔ <b><u>(<code>{len(commands)}</code>) Commands Available</u></b>

🔧 <b>Plugin:</b>  <code>{key}</code>
📘 <b>About:</b>  <code>{plugins[key].about}</code>\n\n"""
            for i, cmd in enumerate(commands, start=1):
                out_str += (f"    🤖 <b>cmd(<code>{i}</code>):</b>  <code>{cmd.name}</code>\n"
                            f"    📚 <b>info:</b>  <i>{cmd.doc}</i>\n\n")
            out_str += f"""📕 <b>Usage:</b>  <code>{Config.CMD_TRIGGER}help [command_name]</code>"""
        else:
            commands = userge.manager.enabled_commands
            key = key.lstrip(Config.CMD_TRIGGER)
            key_ = Config.CMD_TRIGGER + key
            if key in commands:
                out_str = f"<code>{key}</code>\n\n{commands[key].about}"
            elif key_ in commands:
                out_str = f"<code>{key_}</code>\n\n{commands[key_].about}"
            else:
                out_str = f"<i>No Module or Command Found for</i>: <code>{message.input_str}</code>"
    await message.edit(out_str, del_in=0, parse_mode='html')

if Config.BOT_TOKEN and Config.OWNER_ID:
    if Config.HU_STRING_SESSION:
        ubot = userge.bot
    else:
        ubot = userge

    def check_owner(func):
        async def wrapper(_, c_q: CallbackQuery):
            if c_q.from_user and c_q.from_user.id == Config.OWNER_ID:
                await func(c_q)
            else:
                user_dict = await ubot.get_user_dict(Config.OWNER_ID)
                await c_q.answer(
                    f"Only {user_dict['flname']} Can Access this...! Build Your Own @TheUserge 🤘",
                    show_alert=True)
        return wrapper

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"\((.+)\)(next|prev)\((\d+)\)"))
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

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"back\((.+)\)"))
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

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"enter\((.+)\)"))
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

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"((?:un)?load|(?:en|dis)able)\((.+)\)"))
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
            await getattr(flt, task)()
            text, buttons = filter_data(cur_pos)
        else:
            plg = userge.manager.plugins[pos_list[-1]]
            await getattr(plg, task)()
            text, buttons = plugin_data(cur_pos)
        try:
            await callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(buttons))
        except MessageNotModified:
            await callback_query.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"^mm$"))
    @check_owner
    async def callback_mm(callback_query: CallbackQuery):
        await callback_query.edit_message_text(
            "🖥 **Userge Main Menu** 🖥", reply_markup=InlineKeyboardMarkup(main_menu_buttons()))

    @ubot.on_callback_query(filters=Filters.regex(pattern=r"refresh\((.+)\)"))
    @check_owner
    async def callback_exit(callback_query: CallbackQuery):
        cur_pos = str(callback_query.matches[0].group(1))
        pos_list = cur_pos.split('|')
        if len(pos_list) == 4:
            text, buttons = filter_data(cur_pos)
        else:
            text, buttons = plugin_data(cur_pos)
        try:
            await callback_query.edit_message_text(
                text, reply_markup=InlineKeyboardMarkup(buttons))
        except MessageNotModified:
            await callback_query.answer("Nothing Found to Refresh 🤷‍♂️", show_alert=True)

    def is_filter(name: str) -> bool:
        split_ = name.split('.')
        return bool(split_[0] and len(split_) == 2)

    def parse_buttons(page_num: int,
                      cur_pos: str,
                      func: Callable[[str], str],
                      data: Union[List[str], Dict[str, Any]],
                      rows: int = 3):
        buttons = [InlineKeyboardButton(
            func(x), callback_data=f"enter({cur_pos}|{x})".encode()) for x in sorted(data)]
        pairs = list(map(list, zip(buttons[::2], buttons[1::2])))
        if len(buttons) % 2 == 1:
            pairs.append([buttons[-1]])
        max_pages = ceil(len(pairs) / rows)
        current_page = page_num % max_pages
        if len(pairs) > rows:
            pairs = pairs[current_page*rows:(current_page + 1)*rows] + [
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
            if len(cur_pos.split('|')) >= 3:
                tmp_btns.append(InlineKeyboardButton(
                    "🔄 Refresh", callback_data=f"refresh({cur_pos})".encode()))
        return [tmp_btns]

    def category_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plugins = userge.manager.get_all_plugins()[pos_list[1]]
        text = (f"**(`{len(plugins)}`) Plugin(s) Under : "
                f"`{_CATEGORY.get(pos_list[1], '📁')} {pos_list[1]}` 🎭 Category**")
        buttons = parse_buttons(0, '|'.join(pos_list[:2]),
                                lambda x: f"🗃 {x}",
                                plugins)
        return text, buttons

    def plugin_data(cur_pos: str, p_num: int = 0):
        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]
        text = f"""🗃 **--Plugin Status--** 🗃

🎭 **Category** : `{pos_list[1]}`
🔖 **Name** : `{plg.name}`
📝 **About** : `{plg.about}`
✅ **Loaded** : `{plg.is_loaded}`
➕ **Enabled** : `{plg.is_enabled}`
"""
        tmp_btns = []
        if plg.is_loaded:
            tmp_btns.append(InlineKeyboardButton(
                "❎ Unload", callback_data=f"unload({'|'.join(pos_list[:3])})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "✅ Load", callback_data=f"load({'|'.join(pos_list[:3])})".encode()))
        if plg.is_enabled:
            tmp_btns.append(InlineKeyboardButton(
                "➖ Disable", callback_data=f"disable({'|'.join(pos_list[:3])})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "➕ Enable", callback_data=f"enable({'|'.join(pos_list[:3])})".encode()))
        buttons = parse_buttons(p_num, '|'.join(pos_list[:3]),
                                lambda x: f"⚖ {x}" if is_filter(x) else f"⚔ {x}",
                                (flt.name for flt in plg.commands + plg.filters))
        buttons = buttons[:-1] + [tmp_btns] + [buttons[-1]]
        return text, buttons

    def filter_data(cur_pos: str):
        pos_list = cur_pos.split('|')
        plg = userge.manager.plugins[pos_list[2]]
        flts = {flt.name: flt for flt in plg.commands + plg.filters}
        flt = flts[pos_list[-1]]
        if hasattr(flt, 'doc'):
            text = f"""⚔ **--Command Status--** ⚔

🔖 **Name** : `{flt.name}`
📝 **Doc** : `{flt.doc}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.is_loaded}`
➕ **Enabled** : `{flt.is_enabled}`

{flt.about}
"""
        else:
            text = f"""⚖ **--Filter Status--** ⚖

🔖 **Name** : `{flt.name}`
📝 **About** : `{flt.about}`
🤖 **Via Bot** : `{flt.allow_via_bot}`
✅ **Loaded** : `{flt.is_loaded}`
➕ **Enabled** : `{flt.is_enabled}`
"""
        buttons = default_buttons(cur_pos)
        tmp_btns = []
        if flt.is_loaded:
            tmp_btns.append(InlineKeyboardButton(
                "❎ Unload", callback_data=f"unload({cur_pos})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "✅ Load", callback_data=f"load({cur_pos})".encode()))
        if flt.is_enabled:
            tmp_btns.append(InlineKeyboardButton(
                "➖ Disable", callback_data=f"disable({cur_pos})".encode()))
        else:
            tmp_btns.append(InlineKeyboardButton(
                "➕ Enable", callback_data=f"enable({cur_pos})".encode()))
        buttons = [tmp_btns] + buttons
        return text, buttons

    @ubot.on_inline_query()
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
                                url=("https://heroku.com/deploy?template="
                                     "https://github.com/UsergeTeam/Userge/tree/master"))
                        ]
                    ]
                )
            )
        ]
        if inline_query.from_user and inline_query.from_user.id == Config.OWNER_ID:
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
        await inline_query.answer(results=results, cache_time=1)
