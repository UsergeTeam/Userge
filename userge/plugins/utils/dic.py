# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import requests
from userge import userge, Message

LOG = userge.getLogger(__name__)  # logger object

CHANNEL = userge.getCLogger(__name__)  # channel logger object


@userge.on_cmd("dic", about={
    'header': "English Dictionary-telegram",
    'usage': ".dic [word]",
    'examples': 'word : Search for any word'})
async def dictionary(message: Message):
    """this is a dictionary"""
    LOG.info("starting dic command...")
    input_ = message.input_str

    await message.edit("`processing...`")

    def combine(s_word, name):
        w_word = f"🛑<u><b><em>{name.title()}</em></b></u>\n"
        for i in s_word:
            if "definition" in i:
                if "example" in i:
                    w_word += ("\n👩‍🏫<b>Definition:</b>👨‍🏫\n<pre>" + i["definition"] +
                               "</pre>\n\t\t❓<b>Example:</b>❔\n<pre>" + i["example"]+"</pre>")
                else:
                    w_word += "\n👩‍🏫<b>Definition</b>:👨‍🏫\n" +"<pre>"+ i["definition"]+"</pre>"
        w_word += "\n\n"
        return w_word

    def out_print(word1):
        out = ""
        if "meaning" in list(word1):
            meaning = word1["meaning"]
            if "noun" in list(meaning):
                noun = meaning["noun"]
                out += combine(noun, "noun")
                # print(noun)
            if "verb" in list(meaning):
                verb = meaning["verb"]
                out += combine(verb, "verb")
                # print(verb)
            if "preposition" in list(meaning):
                preposition = meaning["preposition"]
                out += combine(preposition, "preposition")
                # print(preposition)
            if "adverb" in list(meaning):
                adverb = meaning["adverb"]
                out += combine(adverb, "adverb")
                # print(adverb)
            if "adjective" in list(meaning):
                adjec = meaning["adjective"]
                out += combine(adjec, "adjective")
                # print(adjec)
            if "abbreviation" in list(meaning):
                abbr = meaning["abbreviation"]
                out += combine(abbr, "abbreviation")
                # print(abbr)
            if "exclamation" in list(meaning):
                exclamation = meaning["exclamation"]
                out += combine(exclamation, "exclamation")
                # print(exclamation)
            if "transitive verb" in list(meaning):
                transitive_verb = meaning["transitive verb"]
                out += combine(transitive_verb, "transitive verb")
                # print(tt)
            if "determiner" in list(meaning):
                determiner = meaning["determiner"]
                out += combine(determiner, "determiner")
                # print(determiner)
            if "crossReference" in list(meaning):
                crosref = meaning["crossReference"]
                out += combine(crosref, "crossReference")
                # print(crosref)
        if "title" in list(word1):
            out += ("<u><code>🔖Error Note:</code></u>\n\n<code>▪️" + word1["title"] +
                    "🥺\n\n▪️" + word1["message"] + "😬\n\n<i>▪️" + word1["resolution"] +
                    "🤓</i></code>")
            # print(l)🥺
        return out

    if not input_:
        await message.edit("<code>❌Plz enter word to search‼️</code>", del_in=5)
    else:
        word = input_
        r_req = requests.get(f"https://api.dictionaryapi.dev/api/v1/entries/en/{word}")
        r_dec = r_req.json()

        v_word = input_
        if isinstance(r_dec, list):
            r_dec = r_dec[0]
            v_word = r_dec['word']
        last_output = out_print(r_dec)
        await message.edit(f"<b>📌Search reasult for    👉 {v_word}\n\n</b>\n"+last_output)
    await CHANNEL.log("request updated!")  # log to channel
