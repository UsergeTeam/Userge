import requests

import json

from userge import userge, Message

from jikanpy import Jikan

from jikanpy.exceptions import APIException

from html_telegraph_poster import TelegraphPoster

jikan = Jikan()

t = TelegraphPoster(use_api=True)

t.create_api_token('userge-X')

async def anime_call_api(search_str):

    query = '''

    query ($id: Int,$search: String) { 

      Media (id: $id, type: ANIME,search: $search) { 

        id

        title {

          romaji

          native

        }

        description (asHtml: false)

        startDate{

            year

          }

          endDate{

            year

          }

          episodes

          chapters

          volumes

          season

          type

          format

          status

          duration

          averageScore

          genres

          bannerImage

          isAdult

          season

          coverImage{

              extraLarge

         }

      }

    }

    '''

    variables = {

        'search' : search_str

    }

    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': variables})

    return response.text

async def formatJSON(outData):

    msg = ""

    jsonData = json.loads(outData)

    res = list(jsonData.keys())

    jsonData = jsonData['data']['Media']

    title_tele = f"{jsonData['title']['romaji']} ({jsonData['title']['native']})"

    if f"{jsonData['bannerImage']}" == "None":

        tele_img = f"{jsonData['coverImage']['extraLarge']}"

    else:

        tele_img = f"{jsonData['bannerImage']}"

    telegra_ph = t.post(title=f"{title_tele}", author='',text=f"<img src='{tele_img}'>{jsonData['description']}")

    if "errors" in res:

        msg += f"Error : {jsonData['errors'][0]['message']}"

    else:

        title = f"[\u200c]({telegra_ph['url']})"

        #titleL = f"{jsonData['title']['romaji']} ({jsonData['title']['native']})"

        link = f"https://anilist.co/anime/{jsonData['id']}"

        title += f"<b>[{title_tele}]({link})</b>"

        msg += title

        msg += f"\n**Type** : <code>{jsonData['format']}</code>"

        if f"{jsonData['isAdult']}" == "True":

           msg += "\n**Rating** : <code>Rx - 18+</code>"

        msg += "\n**Genres** : "

        monog = ", ".join([str(i) for i in jsonData['genres']])

        msg += f"<code>{monog}</code>"

        if f"{jsonData['status']}" == "FINISHED":

           msg += f"\n**Status** : <code>{jsonData['status']} ({jsonData['endDate']['year']})</code>"

        else: 

           msg += f"\n**Status** : <code>{jsonData['status']}</code>"

        msg += f"\n**Episode** : <code>{jsonData['episodes']}</code>"

        msg += f"\n**Premiered ** : <code>{jsonData['season']} {jsonData['startDate']['year']}</code>"

        msg += f"\n**Score** : <code>{jsonData['averageScore']}%</code>"

        msg += f"\n**Duration** : <code>{jsonData['duration']} min</code>"

        Banner = f"[Banner]({jsonData['bannerImage']})"

        Cover = f"[Cover]({jsonData['coverImage']['extraLarge']})"

        if f"{jsonData['coverImage']['extraLarge']}" != "None" and f"{jsonData['bannerImage']}" != "None":

            images = f"\n📷 : {Banner}, {Cover}"

        elif f"{jsonData['bannerImage']}" != "None":   

            images = f"\n📷 : {Banner}"

        elif f"{jsonData['coverImage']['extraLarge']}" != "None":

            images = f"\n📷 : {Cover}"

        else:

            images = ""

        msg += images

    return msg

def replace_text(text):

        return text.replace("\"", "").replace("\\r", "").replace("\\n", "").replace(

            "\\", "")

@userge.on_cmd("ainfo", about={

    'header': "Say it with cute anime girl sticker",

    'usage': "{tr}anime [text | reply to message]",

    'example': "{tr}anime Dragon Ball"})

async def anime_(message: Message):

    """ Search anime """

    query = message.input_or_reply_str

    if not query:

        await message.edit("```Give me text to search Anime```", del_in=3)

        return

    result = await anime_call_api(query)

    msg = await formatJSON(result)

    await message.edit(msg, disable_web_page_preview=False)

@userge.on_cmd("upcomings$", about={'header': "Upcoming anime"})

async def bigf_func(message):

    rep = "<b>Upcoming Anime</b>\n"

    later = jikan.season_later()

    anime = later.get("anime")

    for new in anime:

        name = new.get("title")

        url = new.get("url")

        rep += f"• <a href='{url}'>{name}</a>\n"

        if len(rep) > 1000:

            break

    await message.edit(rep, parse_mode='html', disable_web_page_preview=True)

    

@userge.on_cmd("char", about={

    'header': "Say it with cute anime girl sticker",

    'usage': "{tr}char [text | reply to message]",

    'example': "{tr}char Dragon Ball"})

async def achar_(message: Message):

    """ Search Anime Characters """

    query = message.input_or_reply_str

    if not query:

        await message.edit("```Give me text to search Anime Characters```", del_in=3)

        return

    res = ""

    try:

        search = jikan.search("character", query).get("results")[0].get("mal_id")

    except APIException:

        message.edit("No results found!")

        return ""

    if search:

        try:

            res = jikan.character(search)

        except APIException:

            await message.edit("Error connecting to the API. Please try again!")

            return ""

    if res:

        name = res.get("name")

        kanji = res.get("name_kanji")

        about = res.get("about")

        if len(about) > 1500:

            about = about[:1500] + "..."

        image = res.get("image_url")

        url = res.get("url")

        rep = f"<b>{name} ({kanji})</b>\n\n"

        rep += f"<a href='{image}'>\u200c</a>"

        rep += f"<i>{about}</i>\n"

        rep += f'Read More: <a href="{url}">MyAnimeList</a>'

        await message.edit(replace_text(rep))

@userge.on_cmd("mangas", about={

    'header': "Get details about given manga",

    'usage': "{tr}manga [text | reply to message]",

    'example': "{tr}manga dragon ball"})

async def manga_(message: Message):

    query = message.input_or_reply_str

    if not query:

            await message.edit("```Give manga name!```", del_in=3)

            return

    res = ""

    manga = ""

    try:

        res = jikan.search("manga", query).get("results")[0].get("mal_id")

    except APIException:

        await message.edit("Error connecting to the API. Please try again!")

        return ""

    if res:

        try:

            manga = jikan.manga(res)

        except APIException:

            await message.edit("Error connecting to the API. Please try again!")

            return ""

        title = manga.get("title")

        japanese = manga.get("title_japanese")

        type = manga.get("type")

        status = manga.get("status")

        score = manga.get("score")

        volumes = manga.get("volumes")

        chapters = manga.get("chapters")

        genre_lst = manga.get("genres")

        genres = ""

        for genre in genre_lst:

            genres += genre.get("name") + ", "

        genres = genres[:-2]

        synopsis = manga.get("synopsis")

        image = manga.get("image_url")

        url = manga.get("url")

        url_img = url

        url_img += "/pics"

        rep = f"<b>{title} ({japanese})</b>\n"

        rep += f"<b>Type:</b> <code>{type}</code>\n"

        rep += f"<b>Status:</b> <code>{status}</code>\n"

        rep += f"<b>Genres:</b> <code>{genres}</code>\n"

        rep += f"<b>Score:</b> <code>{score}</code>\n"

        rep += f"<b>Volumes:</b> <code>{volumes}</code>\n"

        rep += f"<b>Chapters:</b> <code>{chapters}</code>\n\n"

        rep += f"<a href='{image}'>\u200c</a>"

        rep += f"<i>{synopsis}</i>"

        rep += f'<a href="{url}"> Read More.</a>'

        await message.edit(rep)

