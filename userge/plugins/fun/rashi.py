import requests
from bs4 import BeautifulSoup
from userge import userge, Message

@userge.on_cmd("rashi", about={
    'header': "Get daily fresh rashifal",
    'usage': "!rashi"})
async def rashi(message: Message):
         csymbol = message.input_str
         symbol = csymbol.lower()
         URL = f"https://www.hamropatro.com/rashifal/daily/{symbol}"
         page = requests.get(URL)
         soup = BeautifulSoup(page.content, "html.parser")
         rashi_div = soup.find_all("div", class_="desc")

         for rashifal in rashi_div:
            request_rashi = rashifal.find("p")
            rashivalue = request_rashi.text.strip()
            await message.edit(rashivalue)