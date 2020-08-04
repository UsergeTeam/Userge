""" Fun Stickers for Tweet """

# By @Krishna_Singhal

import os
import re
import requests

from PIL import Image
from validators.url import url

from userge import userge, Config, Message

CONVERTED_IMG = Config.DOWN_PATH + "img.png"
CONVERTED_STIKR = Config.DOWN_PATH + "sticker.webp"

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "]+")


@userge.on_cmd("trump", about={
    'header': "Custom Sticker of Trump Tweet",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}trump [text | reply to text]"})
async def trump_tweet(msg: Message):
    """ Fun sticker of Trump Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Trump Need some Text for Tweet ð```")
        return
    await msg.edit("```Requesting trump to tweet... ð```")
    await _tweets(msg, text, type_="trumptweet")
    

@userge.on_cmd("modi", about={
    'header': "Custom Sticker of Modi Tweet",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}modi [text | reply to text]"})
async def modi_tweet(msg: Message):
    """ Fun Sticker of Modi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Modi Need some Text for Tweet ð```")
        return
    await msg.edit("```Requesting Modi to tweet... ð```")
    await _tweets(msg, text, "narendramodi")
    

@userge.on_cmd("cmm", about={
    'header': "Custom Sticker of Change My Mind",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}cmm [text | reply to text]"})
async def Change_My_Mind(msg: Message):
    """ Custom Sticker or Banner of Change My Mind """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Need some Text to Change My Mind ð```")
        return
    await msg.edit("```Writing Banner of Change My Mind ð```")
    await _tweets(msg, text, type_="changemymind")
    

@userge.on_cmd("kanna", about={
    'header': "Custom text Sticker of kanna",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}kanna [text | reply to text]"})
async def kanna(msg: Message):
    """ Fun sticker of Kanna """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Kanna Need some text to Write ð```")
        return
    await msg.edit("```Kanna is writing for You ð```")
    await _tweets(msg, text, type_="kannagen")
    

@userge.on_cmd("salmon", about={
    'header': "Custom text Sticker of Salmon Bhai",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}salmon [text | reply to text]"})
async def BeingSalmanKhan(msg: Message):
    """ Fun Sticker of Salmon Bhai Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Salmon Bhai Need some text to Write ð```")
        return
    await msg.edit("```Salmon Bhai is writing for You ð```")
    await _tweets(msg, text, "BeingSalmanKhan")
    
@userge.on_cmd("srk", about={
    'header': "Custom text Sticker of SRK",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}srk [text | reply to text]"})
async def iamsrk(msg: Message):
    """ Fun Sticker of SRK Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```SRK Need some text to Write ð```")
        return
    await msg.edit("```SRK is writing for You ð```")
    await _tweets(msg, text, "iamsrk")
    
@userge.on_cmd("ab", about={
    'header': "Custom text Sticker of Amitabh",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ab [text | reply to text]"})
async def SrBachchan(msg: Message):
    """ Fun Sticker of SrBachchan Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```SrBachchan Need some text to Write ð```")
        return
    await msg.edit("```SrBachchan is writing for You ð```")
    await _tweets(msg, text, "SrBachchan")
    
@userge.on_cmd("ambani", about={
    'header': "Custom text Sticker of Ambani",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ambani [text | reply to text]"})
async def Asliambani(msg: Message):
    """ Fun Sticker of Ambani Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```ambani Need some text to Write ð```")
        return
    await msg.edit("```ambani is writing for You ð```")
    await _tweets(msg, text, "Asliambani")
    
@userge.on_cmd("jio", about={
    'header': "Custom text Sticker of Jio",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}jio [text | reply to text]"})
async def reliancejio(msg: Message):
    """ Fun Sticker of Jio Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Jio Need some text to Write ð```")
        return
    await msg.edit("```Jio is writing for You ð```")
    await _tweets(msg, text, "reliancejio")
    
@userge.on_cmd("ash", about={
    'header': "Custom text Sticker of Ash",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ash [text | reply to text]"})
async def AshwariyaRai(msg: Message):
    """ Fun Sticker of Ash Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Ash Need some text to Write ð```")
        return
    await msg.edit("```Ash is writing for You ð```")
    await _tweets(msg, text, "AshwariyaRai")
    

@userge.on_cmd("rekha", about={
    'header': "Custom text Sticker of Rekha",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}rekha [text | reply to text]"})
async def TheRekhaFanclub(msg: Message):
    """ Fun Sticker of Rekha Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Rekha Need some text to Write ð```")
        return
    await msg.edit("```Rekha is writing for You ð```")
    await _tweets(msg, text, "TheRekhaFanclub")
    
@userge.on_cmd("telegram", about={
    'header': "Custom text Sticker of Telegram",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}telegram [text | reply to text]"})
async def telegram(msg: Message):
    """ Fun Sticker of Telegram Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Telegram Need some text to Write ð```")
        return
    await msg.edit("```Telegram is writing for You ð```")
    await _tweets(msg, text, "telegram")
    
@userge.on_cmd("whatsapp", about={
    'header': "Custom text Sticker of Whatsapp",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}whatsapp [text | reply to text]"})
async def WhatsApp(msg: Message):
    """ Fun Sticker of Whatsapp Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Whatsapp Need some text to Write ð```")
        return
    await msg.edit("```Whatsapp is writing for You ð```")
    await _tweets(msg, text, "WhatsApp")
    
@userge.on_cmd("ananya", about={
    'header': "Custom text Sticker of Ananya",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ananya [text | reply to text]"})
async def ananyapandayy(msg: Message):
    """ Fun Sticker of ananya Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Ananya Need some text to Write ð```")
        return
    await msg.edit("```Ananya is writing for You ð```")
    await _tweets(msg, text, "ananyapandayy")
    
@userge.on_cmd("sonakshi", about={
    'header': "Custom text Sticker of Sonakshi",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}sonakshi [text | reply to text]"})
async def Aslisonagold(msg: Message):
    """ Fun Sticker of Sonakshi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Sonakshi Need some text to Write ð```")
        return
    await msg.edit("```Sonakshi is writing for You ð```")
    await _tweets(msg, text, "Aslisonagold")
    
@userge.on_cmd("sonam", about={
    'header': "Custom text Sticker of Sonam",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}srk [text | reply to text]"})
async def sonamakapoor(msg: Message):
    """ Fun Sticker of Sonam Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Sonam Need some text to Write ð```")
        return
    await msg.edit("```Sonam is writing for You ð```")
    await _tweets(msg, text, "sonamakapoor")
    
@userge.on_cmd("johar", about={
    'header': "Custom text Sticker of Karan Johar",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr} johar [text | reply to text]"})
async def karanjohar(msg: Message):
    """ Fun Sticker of Karan Johar Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Karan Johar Need some text to Write ð```")
        return
    await msg.edit("```Karan Johar is writing for You ð```")
    await _tweets(msg, text, "karanjohar")

@userge.on_cmd("yogi", about={
    'header': "Custom text Sticker of yogi ji",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}yogi [text | reply to text]"})
async def myogiadityanath(msg: Message):
    """ Fun Sticker of  yogi jiweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Yogi Ji Need some text to Write ð```")
        return
    await msg.edit("```Yogi Ji is writing for You ð```")
    await _tweets(msg, text, "myogiadityanath")
    
@userge.on_cmd("ramdev", about={
    'header': "Custom text Sticker of Baba Ramdev",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ramdev [text | reply to text]"})
async def yogrishiramdev(msg: Message):
    """ Fun Sticker of Ramdev Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Ramdev Need some text to Write ð```")
        return
    await msg.edit("```Ramdev is writing for You ð```")
    await _tweets(msg, text, "yogrishiramdev")
    
@userge.on_cmd("sudhir", about={
    'header': "Custom text Sticker of Sudhir",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}sudhir [text | reply to text]"})
async def sudhirchaudhary(msg: Message):
    """ Fun Sticker of Sudhir Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Sudhir Need some text to Write ð```")
        return
    await msg.edit("```Sudhir is writing for You ð```")
    await _tweets(msg, text, "sudhirchaudhary")
    
@userge.on_cmd("arnab", about={
    'header': "Custom text Sticker of Arnab",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}arnab [text | reply to text]"})
async def ArnabGoswamiRTV(msg: Message):
    """ Fun Sticker of Arnab Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Arnab Need some text to Write ð```")
        return
    await msg.edit("```Arnab is writing for You ð```")
    await _tweets(msg, text, "ArnabGoswamiRTV")
    
@userge.on_cmd("rahul", about={
    'header': "Custom text Sticker of rahul",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}rahul [text | reply to text]"})
async def RahulGandhi(msg: Message):
    """ Fun Sticker of Rahul Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Rahul Need some text to Write ð```")
        return
    await msg.edit("```Rahul is writing for You ð```")
    await _tweets(msg, text, "RahulGandhi")
    
@userge.on_cmd("amitshah", about={
    'header': "Custom text Sticker of Amitshah",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}AmitShah [text | reply to text]"})
async def iamsrk(msg: Message):
    """ Fun Sticker of amit shah Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Amit Shah Need some text to Write ð```")
        return
    await msg.edit("```Amit Shah is writing for You ð```")
    await _tweets(msg, text, "AmitShah")
    
@userge.on_cmd("rubika", about={
    'header': "Custom text Sticker of rubika",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}rubika [text | reply to text]"})
async def RubikaLiyaquat(msg: Message):
    """ Fun Sticker of rubika Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```rubika Need some text to Write ð```")
        return
    await msg.edit("```rubika is writing for You ð```")
    await _tweets(msg, text, "RubikaLiyaquat")
    
@userge.on_cmd("amish", about={
    'header': "Custom text Sticker of Amish Devgan",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}amish [text | reply to text]"})
async def AMISHDEVGAN(msg: Message):
    """ Fun Sticker of Amish Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Amish Need some text to Write ð```")
        return
    await msg.edit("```Amish is writing for You ð```")
    await _tweets(msg, text, "AMISHDEVGAN")
    
@userge.on_cmd("deepak", about={
    'header': "Custom text Sticker of deepak",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}deepak [text | reply to text]"})
async def DChaurasia2312(msg: Message):
    """ Fun Sticker of deepak Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```deepak Need some text to Write ð```")
        return
    await msg.edit("```deepak is writing for You ð```")
    await _tweets(msg, text, "DChaurasia2312")
    
@userge.on_cmd("elon", about={
    'header': "Custom text Sticker of elon musk",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}elon [text | reply to text]"})
async def elonmusk(msg: Message):
    """ Fun Sticker of elonmusk Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```elonmusk Need some text to Write ð```")
        return
    await msg.edit("```deepak is writing for You ð```")
    await _tweets(msg, text, "elonmusk")
        
@userge.on_cmd("spacex", about={
    'header': "Custom text Sticker of SpaceX",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}spacex [text | reply to text]"})
async def SpaceX(msg: Message):
    """ Fun Sticker of SpaceX Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```SpaceX Need some text to Write ð```")
        return
    await msg.edit("```deepak is writing for You ð```")
    await _tweets(msg, text, "SpaceX")
        
@userge.on_cmd("isro", about={
    'header': "Custom text Sticker of isro",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}isro [text | reply to text]"})
async def isro(msg: Message):
    """ Fun Sticker of isro Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```isro Need some text to Write ð```")
        return
    await msg.edit("```isro is writing for You ð```")
    await _tweets(msg, text, "isro")
        
@userge.on_cmd("gandhi", about={
    'header': "Custom text Sticker of gandhi",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}gandhi [text | reply to text]"})
async def gandhi(msg: Message):
    """ Fun Sticker of gandhi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```gandhi Need some text to Write ð```")
        return
    await msg.edit("```gandhi is writing for You ð```")
    await _tweets(msg, text, "gandhi")
        
@userge.on_cmd("mia", about={
    'header': "Custom text Sticker of mia",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}mia [text | reply to text]"})
async def miakhalifa(msg: Message):
    """ Fun Sticker of miakhalifa Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```miakhalifa Need some text to Write ð```")
        return
    await msg.edit("```miakhalifa is writing for You ð```")
    await _tweets(msg, text, "miakhalifa")
        
@userge.on_cmd("johnny", about={
    'header': "Custom text Sticker of johnny",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}johnny [text | reply to text]"})
async def JohnnnyyySins(msg: Message):
    """ Fun Sticker of johnny Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```johnny Need some text to Write ð```")
        return
    await msg.edit("```johnny is writing for You ð```")
    await _tweets(msg, text, "JohnnnyyySins")
        
@userge.on_cmd("krk", about={
    'header': "Custom text Sticker of krk",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}krk [text | reply to text]"})
async def kamaalrkhan(msg: Message):
    """ Fun Sticker of krk Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```krk Need some text to Write ð```")
        return
    await msg.edit("```krk is writing for You ð```")
    await _tweets(msg, text, "kamaalrkhan")
        
@userge.on_cmd("vivek", about={
    'header': "Custom text Sticker of vivek",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}vivek [text | reply to text]"})
async def vivekoberoi(msg: Message):
    """ Fun Sticker of vivek Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```vivek Need some text to Write ð```")
        return
    await msg.edit("```vivek is writing for You ð```")
    await _tweets(msg, text, "vivekoberoi")
        
@userge.on_cmd("boring", about={
    'header': "Custom text Sticker of boringcompany",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}boring [text | reply to text]"})
async def boringcompany(msg: Message):
    """ Fun Sticker of boringcompany Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```boringcompany Need some text to Write ð```")
        return
    await msg.edit("```boringcompany is writing for You ð```")
    await _tweets(msg, text, "boringcompany")
        
@userge.on_cmd("sanjay", about={
    'header': "Custom text Sticker of sanjay",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}sanjay [text | reply to text]"})
async def duttsanjay(msg: Message):
    """ Fun Sticker of sanjay Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```sanjay Need some text to Write ð```")
        return
    await msg.edit("```sanjay is writing for You ð```")
    await _tweets(msg, text, "duttsanjay")
        
@userge.on_cmd("ajay", about={
    'header': "Custom text Sticker of ajay",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ajay [text | reply to text]"})
async def ajaydevgn(msg: Message):
    """ Fun Sticker of ajay Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```ajay Need some text to Write ð```")
        return
    await msg.edit("```ajay is writing for You ð```")
    await _tweets(msg, text, "ajaydevgn")
        
@userge.on_cmd("tesla", about={
    'header': "Custom text Sticker of tesla",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}tesla [text | reply to text]"})
async def tesla(msg: Message):
    """ Fun Sticker of tesla Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```tesla Need some text to Write ð```")
        return
    await msg.edit("```tesla is writing for You ð```")
    await _tweets(msg, text, "tesla")
        
@userge.on_cmd("albert", about={
    'header': "Custom text Sticker of albert",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}albert [text | reply to text]"})
async def AlbertEinstein(msg: Message):
    """ Fun Sticker of albert Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```albert Need some text to Write ð```")
        return
    await msg.edit("```albert is writing for You ð```")
    await _tweets(msg, text, "AlbertEinstein")
        
@userge.on_cmd("bear", about={
    'header': "Custom text Sticker of BearGrylls",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}bear [text | reply to text]"})
async def BearGrylls(msg: Message):
    """ Fun Sticker of BearGrylls Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```BearGrylls Need some text to Write ð```")
        return
    await msg.edit("```BearGrylls is writing for You ð```")
    await _tweets(msg, text, "BearGrylls")
        
@userge.on_cmd("rajni", about={
    'header': "Custom text Sticker of rajinikanth",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}rajni [text | reply to text]"})
async def rajinikanth(msg: Message):
    """ Fun Sticker of rajinikanth Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```rajinikanth Need some text to Write ð```")
        return
    await msg.edit("```rajinikanth is writing for You ð```")
    await _tweets(msg, text, "rajinikanth")
        
@userge.on_cmd("apple", about={
    'header': "Custom text Sticker of apple",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}apple [text | reply to text]"})
async def apple(msg: Message):
    """ Fun Sticker of apple Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```apple Need some text to Write ð```")
        return
    await msg.edit("```apple is writing for You ð```")
    await _tweets(msg, text, "apple")
        
@userge.on_cmd("durov", about={
    'header': "Custom text Sticker of durov",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}durov [text | reply to text]"})
async def durov(msg: Message):
    """ Fun Sticker of durov Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```durov Need some text to Write ð```")
        return
    await msg.edit("```durov is writing for You ð```")
    await _tweets(msg, text, "durov")
        
@userge.on_cmd("fb", about={
    'header': "Custom text Sticker of facebook",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}fb [text | reply to text]"})
async def facebook(msg: Message):
    """ Fun Sticker of facebook Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```facebook Need some text to Write ð```")
        return
    await msg.edit("```facebook is writing for You ð```")
    await _tweets(msg, text, "facebook")
        
@userge.on_cmd("bjp", about={
    'header': "Custom text Sticker of bjp",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}bjp [text | reply to text]"})
async def bjp4india(msg: Message):
    """ Fun Sticker of bjp Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```bjp Need some text to Write ð```")
        return
    await msg.edit("```bjp is writing for You ð```")
    await _tweets(msg, text, "bjp4india")
        
@userge.on_cmd("sambit", about={
    'header': "Custom text Sticker of sambit",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}sambit [text | reply to text]"})
async def sambitswaraj(msg: Message):
    """ Fun Sticker of rajinikanth Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```sambit Need some text to Write ð```")
        return
    await msg.edit("```sambit is writing for You ð```")
    await _tweets(msg, text, "sambitswaraj")
        
@userge.on_cmd("nirmala", about={
    'header': "Custom text Sticker of nirmala",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}nirmala [text | reply to text]"})
async def nsitharaman(msg: Message):
    """ Fun Sticker of nirmala Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```nirmala Need some text to Write ð```")
        return
    await msg.edit("```nirmala is writing for You ð```")
    await _tweets(msg, text, "nsitharaman")
        
@userge.on_cmd("youtube", about={
    'header': "Custom text Sticker of youtube",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}youtube [text | reply to text]"})
async def youtube(msg: Message):
    """ Fun Sticker of youtube Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```youtube Need some text to Write ð```")
        return
    await msg.edit("```youtube is writing for You ð```")
    await _tweets(msg, text, "youtube")
        
@userge.on_cmd("tiktok", about={
    'header': "Custom text Sticker of tiktok",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}tiktok [text | reply to text]"})
async def tiktok_in(msg: Message):
    """ Fun Sticker of tiktok Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```tiktok Need some text to Write ð```")
        return
    await msg.edit("```tiktok is writing for You ð```")
    await _tweets(msg, text, "tiktok_in")
        
@userge.on_cmd("googal", about={
    'header': "Custom text Sticker of google",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}googal [text | reply to text]"})
async def google(msg: Message):
    """ Fun Sticker of google Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```google Need some text to Write ð```")
        return
    await msg.edit("```google is writing for You ð```")
    await _tweets(msg, text, "google")
        
@userge.on_cmd("kangana", about={
    'header': "Custom text Sticker of kangana",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}kangana [text | reply to text]"})
async def thekangana(msg: Message):
    """ Fun Sticker of kangana Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```kangana Need some text to Write ð```")
        return
    await msg.edit("```kangana is writing for You ð```")
    await _tweets(msg, text, "thekangana")
        
@userge.on_cmd("hrithik", about={
    'header': "Custom text Sticker of hrithik",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}hrithik [text | reply to text]"})
async def ihrithik(msg: Message):
    """ Fun Sticker of hrithik Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```hrithik Need some text to Write ð```")
        return
    await msg.edit("```hrithik is writing for You ð```")
    await _tweets(msg, text, "ihrithik")
        
@userge.on_cmd("nirmal", about={
    'header': "Custom text Sticker of nirmalbabaji",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}nirmal [text | reply to text]"})
async def nirmalbabaji(msg: Message):
    """ Fun Sticker of nirmalbabaji Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```nirmalbabaji Need some text to Write ð```")
        return
    await msg.edit("```nirmalbabaji is writing for You ð```")
    await _tweets(msg, text, "nirmalbabaji")
        
@userge.on_cmd("ramrahim", about={
    'header': "Custom text Sticker of ram rahim singh",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}ramrahim [text | reply to text]"})
async def gurmeetHoneyS(msg: Message):
    """ Fun Sticker of ram rahim singh Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```ram rahim singh Need some text to Write ð```")
        return
    await msg.edit("```ram rahim singh is writing for You ð```")
    await _tweets(msg, text, "gurmeetHoneyS")
        
@userge.on_cmd("cook", about={
    'header': "Custom text Sticker of tim cook",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}cook [text | reply to text]"})
async def tim_cook(msg: Message):
    """ Fun Sticker of tim cook Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```tim coom Need some text to Write ð```")
        return
    await msg.edit("```tim cook is writing for You ð```")
    await _tweets(msg, text, "tim_cook")
        
@userge.on_cmd("steve", about={
    'header': "Custom text Sticker of steve jobs",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}steve [text | reply to text]"})
async def stevejobsceo(msg: Message):
    """ Fun Sticker of steve Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```steve Need some text to Write ð```")
        return
    await msg.edit("```steve is writing for You ð```")
    await _tweets(msg, text, "stevejobsceo")
            
@userge.on_cmd("starbucks", about={
    'header': "Custom text Sticker of Starbucks",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}starbucks [text | reply to text]"})
async def starbucks(msg: Message):
    """ Fun Sticker of starbucks Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```starbucks Need some text to Write ð```")
        return
    await msg.edit("```starbucks is writing for You ð```")
    await _tweets(msg, text, "starbucks")
    
@userge.on_cmd("netflix", about={
    'header': "Custom text Sticker of netflix",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}netflix [text | reply to text]"})
async def netflix(msg: Message):
    """ Fun Sticker of netflix Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```netflix Need some text to Write ð```")
        return
    await msg.edit("```netflix is writing for You ð```")
    await _tweets(msg, text, "netflix")
    
@userge.on_cmd("prime", about={
    'header': "Custom text Sticker of PrimeVideo",
    'flags': {
        '-s': "To get tweet in PrimeVideo"},
    'usage': "{tr}prime [text | reply to text]"})
async def PrimeVideo(msg: Message):
    """ Fun Sticker of PrimeVideo Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```PrimeVideo Need some text to Write ð```")
        return
    await msg.edit("```PrimeVideo is writing for You ð```")
    await _tweets(msg, text, "PrimeVideo")
    
@userge.on_cmd("altbalaji", about={
    'header': "Custom text Sticker of altbalaji",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}altbalaji [text | reply to text]"})
async def altbalaji(msg: Message):
    """ Fun Sticker of altbalaji Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```altbalaji Need some text to Write ð```")
        return
    await msg.edit("```altbalaji is writing for You ð```")
    await _tweets(msg, text, "altbalaji")
    
@userge.on_cmd("general", about={
    'header': "Custom text Sticker of GeneralBakshi",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}general [text | reply to text]"})
async def GeneralBakshi(msg: Message):
    """ Fun Sticker of GeneralBakshi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```GeneralBakshi Need some text to Write ð```")
        return
    await msg.edit("```GeneralBakshi is writing for You ð```")
    await _tweets(msg, text, "GeneralBakshi")
    
@userge.on_cmd("mdh", about={
    'header': "Custom text Sticker of Mdhmasalauncle",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}mdh [text | reply to text]"})
async def Mdhmasalauncle(msg: Message):
    """ Fun Sticker of Mdhmasalauncle Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Mdhmasalauncle Need some text to Write ð```")
        return
    await msg.edit("```Mdhmasalauncle is writing for You ð```")
    await _tweets(msg, text, "Mdhmasalauncle")
    
@userge.on_cmd("setu", about={
    'header': "Custom text Sticker of Arogyasetu",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}setu [text | reply to text]"})
async def Arogyasetu(msg: Message):
    """ Fun Sticker of Arogyasetu Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Arogyasetu Need some text to Write ð```")
        return
    await msg.edit("```Arogyasetu is writing for You ð```")
    await _tweets(msg, text, "Arogyasetu")
    
@userge.on_cmd("pornhub", about={
    'header': "Custom text Sticker of pornhub",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}pornhub [text | reply to text]"})
async def pornhub(msg: Message):
    """ Fun Sticker of pornhub Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```pornhub Need some text to Write ð```")
        return
    await msg.edit("```pornhub is writing for You ð```")
    await _tweets(msg, text, "pornhub")
    
@userge.on_cmd("davood", about={
    'header': "Custom text Sticker of Davood_Official",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}davood [text | reply to text]"})
async def Davood_Official(msg: Message):
    """ Fun Sticker of Davood_Official Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Davood_Official Need some text to Write ð```")
        return
    await msg.edit("```Davood_Official is writing for You ð```")
    await _tweets(msg, text, "Davood_Official")
    
@userge.on_cmd("osama", about={
    'header': "Custom text Sticker of ItstherealOsama",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}osama [text | reply to text]"})
async def ItstherealOsama(msg: Message):
    """ Fun Sticker of ItstherealOsama Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```ItstherealOsama Need some text to Write ð```")
        return
    await msg.edit("```ItstherealOsama is writing for You ð```")
    await _tweets(msg, text, "ItstherealOsama")
    
@userge.on_cmd("kim", about={
    'header': "Custom text Sticker of Real_kimjonguno",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}kim [text | reply to text]"})
async def Real_kimjonguno(msg: Message):
    """ Fun Sticker of Real_kimjonguno Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Real_kimjonguno Need some text to Write ð```")
        return
    await msg.edit("```Real_kimjonguno is writing for You ð```")
    await _tweets(msg, text, "Real_kimjonguno")
    
@userge.on_cmd("imran", about={
    'header': "Custom text Sticker of ImranKhanPTI",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}imran [text | reply to text]"})
async def ImranKhanPTI(msg: Message):
    """ Fun Sticker of ImranKhanPTI Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```ImranKhanPTI Need some text to Write ð```")
        return
    await msg.edit("```ImranKhanPTI is writing for You ð```")
    await _tweets(msg, text, "ImranKhanPTI")
    
@userge.on_cmd("emraan", about={
    'header': "Custom text Sticker of emraanhashmi",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}emraan [text | reply to text]"})
async def emraanhashmi(msg: Message):
    """ Fun Sticker of emraanhashmi Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```emraanhashmi Need some text to Write ð```")
        return
    await msg.edit("```emraanhashmi is writing for You ð```")
    await _tweets(msg, text, "emraanhashmi")
    
@userge.on_cmd("vijay", about={
    'header': "Custom text Sticker of TheVijayMallya",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}vijay [text | reply to text]"})
async def TheVijayMallya(msg: Message):
    """ Fun Sticker of TheVijayMallya Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```TheVijayMallya Need some text to Write ð```")
        return
    await msg.edit("```TheVijayMallya is writing for You ð```")
    await _tweets(msg, text, "TheVijayMallya")
                  
@userge.on_cmd("android", about={
    'header': "Custom text Sticker of Android jobs",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}android [text | reply to text]"})
async def Android(msg: Message):
    """ Fun Sticker of Android Tweet """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("```Android Need some text to Write ð```")
        return
    await msg.edit("```Android is writing for You ð```")
    await _tweets(msg, text, "Android")
                        
@userge.on_cmd("tweet", about={
    'header': "Tweet With Custom text Sticker",
    'flags': {
        '-s': "To get tweet in Sticker"},
    'usage': "{tr}tweet Text , Username\n"
             "{tr}tweet Text\n"
             "{tr}tweet [Text | with reply to User]"})
async def tweet(msg: Message):
    """ Tweet with your own Username """
    replied = msg.reply_to_message
    text = msg.filtered_input_str
    if replied and not text:
        text = replied.text
    if not text:
        await msg.err("Give Me some text to Tweet 😕")
        return
    username = ''
    if ',' in text:
        text, username = text.split(',')
    if not username:
        if replied:
            username = replied.from_user.username or replied.from_user.first_name
        else:
            username = msg.from_user.username or msg.from_user.first_name
    await msg.edit("```Creating a Tweet Sticker 😏```")
    await _tweets(msg, text.strip(), username.strip())


def _deEmojify(inputString: str) -> str:
    """Remove emojis and other non-safe characters from string"""
    return re.sub(EMOJI_PATTERN, '', inputString)


async def _tweets(msg: Message, text: str, username: str = '', type_: str = "tweet") -> None:
    api_url = f"https://nekobot.xyz/api/imagegen?type={type_}&text={_deEmojify(text)}"
    if username:
        api_url += f"&username={_deEmojify(username)}"
    res = requests.get(api_url).json()
    tweets_ = res.get("message")
    if not url(tweets_):
        await msg.err("Invalid Syntax, Exiting...")
        return
    tmp_file = Config.DOWN_PATH + "temp.png"
    with open(tmp_file, "wb") as t_f:
        t_f.write(requests.get(tweets_).content)
    img = Image.open(tmp_file)
    img.save(CONVERTED_IMG)
    img.save(CONVERTED_STIKR)
    await msg.delete()
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else None
    if '-s' in msg.flags:
        await msg.client.send_sticker(chat_id=msg.chat.id,
                                      sticker=CONVERTED_STIKR,
                                      reply_to_message_id=msg_id)
    else:
        await msg.client.send_photo(chat_id=msg.chat.id,
                                    photo=CONVERTED_IMG,
                                    reply_to_message_id=msg_id)
    os.remove(tmp_file)
    os.remove(CONVERTED_IMG)
    os.remove(CONVERTED_STIKR)
