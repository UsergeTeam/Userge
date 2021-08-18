import requests
from bs4 import BeautifulSoup
from userge import userge, Message

@userge.on_cmd("td", about={
    'header': "Tell present nepali date",
    'usage': "!td"})
async def nepdate(message: Message):
         nefoli = []
         URL = "https://www.hamropatro.com/"
         page = requests.get(URL)
         soup = BeautifulSoup(page.content, "html.parser")
         time_div = soup.find_all("div", class_ = "time")
         date_div = soup.find_all("div", class_ = "date")

         for date in date_div:
             request_date = date.find(class_='nep')
             datevalue = request_date.text.strip()
             nefoli.append(datevalue)
             break;

         event_div = soup.find(class_ = "events")
         eventvalue1 = event_div.text.strip()
         nefoli.append(eventvalue1)

   
         for time in time_div:
             request_time = time.find("span")
             engdate = time.find("span", class_ = "eng")
             timevalue = request_time.text.strip() + "\n" + engdate.text.strip()

             nefoli.append(timevalue)
             break;
         todaynefol = '\n'.join(nefoli)   
         await message.edit(todaynefol)
  