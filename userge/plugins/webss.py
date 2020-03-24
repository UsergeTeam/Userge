from userge import userge, Message
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import time
import os

profile = webdriver.FirefoxProfile()
profile.accept_untrusted_certs = True
options = Options()
options.headless = True
options.set_capability("marionette", False)


@userge.on_cmd("webss", about="__Get snapshot of a website__")
async def webss(message: Message):
    await message.edit("`Processing`")
    try:
        path = await getimg(message.input_str)
    except Exception as e:
        await message.err(str(e), del_in=10)
    else:
        await userge.send_document(message.chat.id, path, caption=message.input_str)
        if os.path.isfile(path):
            os.remove(path)
        await message.delete()


async def getimg(url):
    driver = webdriver.Firefox(executable_path='resources/geckodriver',
                               options=options,
                               firefox_profile=profile)
    try:
        driver.get(url)
    except Exception:
        raise
    else:
        path = f'./screenshot/{time()}screenshot.png'
        driver.save_screenshot(path)
        return path
    finally:
        driver.quit()
