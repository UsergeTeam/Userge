""" enjoy word_emoji """

# by @krishna_singhal

from userge import userge, Message


@userge.on_cmd("hii", about={
    'header': "Use HI to greet someone",
    'usage': "{tr}hii [foreground emoji] , [background emoji]"})
async def hii_(message: Message):
    """hii"""
    if not message.input_str:
        await message.edit("```That's why u Peru ,```", del_in=5)
        return
    if ',' not in message.input_str:
        await message.edit("```Two emoji required as foreground , background ```", del_in=5)
        return
    paytext, filler = message.input_str.split(',', maxsplit=1)
    if not filler:
        awat message.edit("```Second emoji not found ...```", del_in=5)
        return
    paytext = paytext.strip()
    filler = filler.strip()
    pay = "{}\n{}\n{}\n{}\n{}".format(
        paytext + filler * 2 + paytext +
        filler + paytext * 3,
        paytext + filler * 2 + paytext +
        filler * 2 + paytext + filler,
        paytext * 4 + filler * 2 + paytext + filler,
        paytext + filler * 2 + paytext +
        filler * 2 + paytext + filler,
        paytext + filler * 2 + paytext +
        filler + paytext * 3)
    await message.edit(pay)


@userge.on_cmd("lol", about={
    'header': "Lol also known as lots of laugh used to indicate "
              "smiling or slight amusement",
    'usage': "{tr}lol [foreground emoji] , [background emoji]"})
async def lol_(message: Message):
    """lol"""
    if not message.input_str:
        await message.edit("```That's why u Peru ,```", del_in=5)
        return
    if ',' not in message.input_str:
        await message.edit("```Two emoji required as foreground , background ```", del_in=5)
        return
    paytext, filler = message.input_str.split(',', maxsplit=1)
    if not filler:
        awat message.edit("```Second emoji not found ...```", del_in=5)
        return
    paytext = paytext.strip()
    filler = filler.strip()
    pay = "{}\n{}\n{}\n{}".format(
        paytext + filler * 3 +
        paytext * 3 + filler + paytext + filler * 2,
        paytext + filler * 3 +
        paytext + filler + paytext + filler +
        paytext + filler * 2,
        paytext + filler * 3 + paytext + filler +
        paytext + filler + paytext + filler * 2,
        paytext * 3 + filler + paytext * 3 + filler + paytext * 3)
    await message.edit(pay)


@userge.on_cmd("wtf", about={
    'header': "WTF Generally stands for 'What the fuck' use for fun",
    'usage': "{tr}wtf [foreground emoji] , [background emoji]"})
async def wtf_(message: Message):
    """wtf"""
    if not message.input_str:
        await message.edit("```That's why u Peru ,```", del_in=5)
        return
    if ',' not in message.input_str:
        await message.edit("```Two emoji required as foreground , background ```", del_in=5)
        return
    paytext, filler = message.input_str.split(',', maxsplit=1)
    if not filler:
        await message.edit("```Second emoji not found ...```", del_in=5)
        return
    paytext = paytext.strip()
    filler = filler.strip()
    pay = "{}\n{}\n{}\n{}".format(
        paytext + filler * 3 + paytext +
        filler + paytext * 3 + filler + paytext * 3,
        paytext + filler + paytext + filler + paytext +
        filler * 2 + paytext + filler * 2 + paytext + filler * 2,
        paytext * 2 + filler + paytext * 2 + filler * 2 + paytext +
        filler * 2 + paytext * 2 + filler,
        paytext + filler * 3 + paytext + filler * 2 + paytext + filler * 2 + paytext + filler * 2)
    await message.edit(pay)
