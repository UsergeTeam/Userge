import re
import time
import random
from userge import userge, Message

UWUS = (
    'ÓwÓ',
    'ÕwÕ',
    '@w@',
    'ØwØ',
    'øwø',
    'uwu',
    '◕w◕',
    '◔w◔',
    'ʘwʘ',
    '⓪w⓪',
    '(owo)',
    '(。O ω O。)',
    '(。O⁄ ⁄ω⁄ ⁄ O。)',
    '(O ᵕ O)',
    '(O꒳O)',
    'ღ(O꒳Oღ)',
    '♥(。ᅌ ω ᅌ。)',
    '(ʘωʘ)',
    '(⁄ʘ⁄ ⁄ ω⁄ ⁄ ʘ⁄)♡',
    '( ͡o ω ͡o )',
    '( ͡o ᵕ ͡o )',
    '( ͡o ꒳ ͡o )',
    '( o͡ ꒳ o͡ )',
    '( °꒳° )',
    '( °ᵕ° )',
    '( °﹏° )',
    '( °ω° )',
    '̷(ⓞ̷ ̷꒳̷ ̷ⓞ̷)',
    '（ ゜ω 。）'
)

FACEREACTS = (
    "ʘ‿ʘ",
    "ヾ(-_- )ゞ",
    "(っ˘ڡ˘ς)",
    "(´ж｀ς)",
    "( ಠ ʖ̯ ಠ)",
    "(° ͜ʖ͡°)╭∩╮",
    "(ᵟຶ︵ ᵟຶ)",
    "(งツ)ว",
    "ʚ(•｀",
    "(っ▀¯▀)つ",
    "(◠﹏◠)",
    "( ͡ಠ ʖ̯ ͡ಠ)",
    "( ఠ ͟ʖ ఠ)",
    "(∩｀-´)⊃━☆ﾟ.*･｡ﾟ",
    "(⊃｡•́‿•̀｡)⊃",
    "(._.)",
    "{•̃_•̃}",
    "(ᵔᴥᵔ)",
    "♨_♨",
    "⥀.⥀",
    "ح˚௰˚づ ",
    "(҂◡_◡)",
    "ƪ(ړײ)‎ƪ​​",
    "(っ•́｡•́)♪♬",
    "◖ᵔᴥᵔ◗ ♪ ♫ ",
    "(☞ﾟヮﾟ)☞",
    "[¬º-°]¬",
    "(Ծ‸ Ծ)",
    "(•̀ᴗ•́)و ̑̑",
    "ヾ(´〇`)ﾉ♪♪♪",
    "(ง'̀-'́)ง",
    "ლ(•́•́ლ)",
    "ʕ •́؈•̀ ₎",
    "♪♪ ヽ(ˇ∀ˇ )ゞ",
    "щ（ﾟДﾟщ）",
    "( ˇ෴ˇ )",
    "눈_눈",
    "(๑•́ ₃ •̀๑) ",
    "( ˘ ³˘)♥ ",
    "ԅ(≖‿≖ԅ)",
    "♥‿♥",
    "◔_◔",
    "⁽⁽ଘ( ˊᵕˋ )ଓ⁾⁾",
    "乁( ◔ ౪◔)「      ┑(￣Д ￣)┍",
    "( ఠൠఠ )ﾉ",
    "٩(๏_๏)۶",
    "┌(ㆆ㉨ㆆ)ʃ",
    "ఠ_ఠ",
    "(づ｡◕‿‿◕｡)づ",
    "(ノಠ ∩ಠ)ノ彡( \\o°o)\\",
    "“ヽ(´▽｀)ノ”",
    "༼ ༎ຶ ෴ ༎ຶ༽",
    "｡ﾟ( ﾟஇ‸இﾟ)ﾟ｡",
    "(づ￣ ³￣)づ",
    "(⊙.☉)7",
    "ᕕ( ᐛ )ᕗ",
    "t(-_-t)",
    "(ಥ⌣ಥ)",
    "ヽ༼ ಠ益ಠ ༽ﾉ",
    "༼∵༽ ༼⍨༽ ༼⍢༽ ༼⍤༽",
    "ミ●﹏☉ミ",
    "(⊙_◎)",
    "¿ⓧ_ⓧﮌ",
    "ಠ_ಠ",
    "(´･_･`)",
    "ᕦ(ò_óˇ)ᕤ",
    "⊙﹏⊙",
    "(╯°□°）╯︵ ┻━┻",
    "¯\\_(⊙︿⊙)_/¯",
    "٩◔̯◔۶",
    "°‿‿°",
    "ᕙ(⇀‸↼‶)ᕗ",
    "⊂(◉‿◉)つ",
    "V•ᴥ•V",
    "q(❂‿❂)p",
    "ಥ_ಥ",
    "ฅ^•ﻌ•^ฅ",
    "ಥ﹏ಥ",
    "（ ^_^）o自自o（^_^ ）",
    "ಠ‿ಠ",
    "ヽ(´▽`)/",
    "ᵒᴥᵒ#",
    "( ͡° ͜ʖ ͡°)",
    "┬─┬﻿ ノ( ゜-゜ノ)",
    "ヽ(´ー｀)ノ",
    "☜(⌒▽⌒)☞",
    "ε=ε=ε=┌(;*´Д`)ﾉ",
    "(╬ ಠ益ಠ)",
    "┬─┬⃰͡ (ᵔᵕᵔ͜ )",
    "┻━┻ ︵ヽ(`Д´)ﾉ︵﻿ ┻━┻",
    "¯\\_(ツ)_/¯",
    "ʕᵔᴥᵔʔ",
    "(`･ω･´)",
    "ʕ•ᴥ•ʔ",
    "ლ(｀ー´ლ)",
    "ʕʘ̅͜ʘ̅ʔ",
    "（　ﾟДﾟ）",
    "¯\\(°_o)/¯",
    "(｡◕‿◕｡)",
)


@userge.on_cmd("[Ss]hg",
               about="__shrugger__",
               name="shg",
               trigger='')
async def shg_(message: Message):

    await message.edit("¯¯\\__(ツ)__/¯¯", parse_mode='html')


@userge.on_cmd("react", about="__React to a message__")
async def react_(message: Message):

    await message.edit(random.choice(FACEREACTS), parse_mode='html')


@userge.on_cmd("[Kk]ek",
               about="__:/__",
               name="kek",
               trigger='')
async def kek_(message: Message):
    uio = ["/", "\\"]
    for i in range(1, 15):
        time.sleep(0.3)

        await message.edit(":" + uio[i % 2])


@userge.on_cmd("[Ll]ol",
               about="__-_-__",
               name="lol",
               trigger='')
async def lol_(message: Message):
    okay = r"-_ "
    for _ in range(10):
        okay = okay[:-1] + r"_-"

        await message.edit(okay, parse_mode='html')


@userge.on_cmd("[Oo]of",
               about="__`oof`s more dramatic__",
               name="oof",
               trigger='')
async def oof_(message: Message):
    t = "Oo "
    for _ in range(10):
        t = t[:-1] + "of"

        await message.edit(t)


@userge.on_cmd("clap", about="""\
__Claps for the selected message__

**Usage:**

    `.clap [text | reply to msg]`""")
async def clap_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    await message.edit(f"👏 {re.sub(r' +', ' 👏 ', text)} 👏")


@userge.on_cmd("[Oo]wo",
               about="""\
__UwU's you OwO__

**Usage:**

    `owo [text | reply to msg]`""",
               name="owo",
               trigger='')
async def faces_(message: Message):
    text = message.input_str
    if message.reply_to_message:
        text = message.reply_to_message.text

    text = re.sub(r"([rl])", "w", text)
    text = re.sub(r"([RL])", "W", text)
    text = re.sub(r"n([aeiou])", r"ny\1", text)
    text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", text)
    text = re.sub(r"!", " " + random.choice(UWUS), text)
    text = text.replace("ove", "uv")
    text += " " + random.choice(UWUS)

    await message.edit(text.strip(), parse_mode='html')
