import aiohttp, pylast, os
from userge import get_collection, userge
from random import choice as rand_array


class Config:
    LASTFM_API_KEY = os.environ.get("FM_API")
    LASTFM_SECRET = os.environ.get("FM_SECRET")
    LASTFM_PASSWORD = os.environ.get("FM_PASSWORD")
    LASTFM_USERNAME = os.environ.get("FM_USERNAME")


du = "https://last.fm/user/"
tglst_ = ["rock","electronic","alternative","indie","pop","metal","jazz","classic_rock","ambient","experimental","folk","punk","indie_rock","hip_hop","hard_rock","instrumental","black_metal","dance","80s","death_metal","heavy_metal","hardcore","british","soul","chillout","electronica","rap","classical","industrial","soundtrack","punk_rock","blues","thrash_metal", "90s","acoustic","metalcore","psychedelic","japanese","post_rock","german","funk","new_wave","trance","j_pop","ballad","1980s","1990s","70s","1970s","2000s","2010s","anime","beat","beats","nightcore","hiphop","trap","dj","culture","electro","edm","dubstep","bass","art_punk","britpunk","college_rock","crust_punk","folk_punk","grunge","hardcore_punk","lo_fi","shoegaze","steampunk","acoustic_blues","african_blues","blues_rock","blues_shouter","british_blues","canadian_blues","chicago_blues","classic_blues","country_blues","dark_blues","delta_blues","detroit_blues","doom_blues","electric_blues","folk_blues","gospel_blues","harmonica_blues","hokum_blues","jazz_blues","jump_blues","louisiana_blues","memphis_blues","modern_blues","ny_blues","piano_blues","piedmont_blues","punk_blues","ragtime_blues","rhythm_blues","soul_blues","swamp_blues","st._louis_blues","texas_blues","urban_blues","vandeville","zydeco","lullabies","sing_along","stories","avant_garde","ballet","baroque","cantata","chamber_music","string_quartet","chant","choral","concerto","concerto_grosso","early_music","expressionist","high_classical","impressionist","mass_requiem","medieval","minimalism","opera","oratorio","orchestral","organum","renaissance","romantic","sonata","symphonic","symphony","wedding_music","comedy","novelty","parody_music","stand_up_comedy","vaudeville","commercial","jingles","tv_themes","country","americana","bluegrass","blues_country","classic_country","close_harmony","country_gospel","country_pop","country_rap","country_rock","country_soul","cowpunk","dansband","honky_tonk","franco_country","hellbilly_music","lubbock_sound","nashville_sound","outlaw_country","progressive","red_dirt","sertanejo","texas_county","urban_cowboy","western_swing","breakcore","4_beat","acid_breaks","baltimore_club","big_beat","broken_beat","florida_breaks","nu_skool_breaks","brostep","chillstep","deep_house","electro_house","electroswing","exercise","future_garage","garage","glitch_hop","glitch_pop","grime","bouncy_house","bouncy_techno","doomcore","dubstyle","gabber","happy_hardcore","hardstyle","jumpstyle","makina","speedcore","terrorcore","uk_hardcore","hard_dance","horrorcore","house","acid_house","chicago_house","diva_house","dutch_house","freestyle_house","french_house","funky_house","ghetto_house","hardbag","hip_house","italo_house","latin_house","minimal_house","rave_music","swing_house","uk_hard_house","us_garage","vocal_house","jackin_house","liquid_du","regstep","techno","acid_techno","detroit_techno","free_tekno","ghettotech","minimal","nortec","schranz","techno_dnb","technopop","tecno_brega","toytown_techno","acid_trance","classic_trance","dream_trance","goa_trance","dark_psytrance","full_on","psybreaks","psyprog","suomisaundi","hard_trance","tech_trance","vocal_trance","disney","easy_listening","background","bop","elevator","furniture","lounge","swing","2_step","ambient_dub","ambient_house","ambient_techno","dark_ambient","drone_music","illbient","isolationism","lowercase","bassline","chillwav","chiptune","bitpop","game_boy","nintendocore","crunk","downtempo","acid_jazz","balearic_beat","chill_out","dub_music","dubtronica","moombahton","nu_jazz","trip_hop","drum_&_bass","darkcore","darkstep","drumfunk","drumstep","hardstep","jump_up","liquid_funk","neurofunk","darkside_jungle","ragga_jungle","raggacore","sambass","techstep","electro_grime","electropop","electro_swing","electroacoustic","computer_music","field_recording","live_coding","tape_music","berlin_school","chillwave","folktronica","freestyle_music","glitch","idm","laptronica","skweee","sound_art","synthcore","electronic_rock","baggy","madchester","dance_punk","dance_rock","dark_wave","electroclash","electronicore","electropunk","ethereal_wave","indietronica","new_rave","space_rock","synthpop","synthpunk","eurodance","bubblegum_dance","italo_dance","turbofolk","hi_nrg","eurobeat","hard_nrg","new_beat","uk_garage","4×4","speed_garage","enka","french_pop","folk_music","anti_folk","filk_music","freak_folk","indie_folk","industrial_folk","neofolk","sung_poetry","techno_folk","german_folk","german_pop","alternative_rap","bounce","chap_hop","crunkcore","cumbia_rap","dirty_south","east_coast","brick_city_club","mafioso_rap","freestyle_rap","g_funk","gangsta_rap","golden_age","hardcore_rap","hip_pop","hyphy","jazz_rap","latin_rap","low_bap","lyrical_hip_hop","merenrap","midwest_hip_hop","chicago_hip_hop","detroit_hip_hop","motswako","nerdcore","new_jack_swing","old_school_rap","turntablism","underground_rap","west_coast_rap","holiday","chanukah","christmas","children’s","classic","modern","r&b","religious","easter","halloween","other","thanksgiving","indie_pop","aggrotech","coldwave","cybergrind","dark_electro","futurepop","industrial_rock","noise","japanoise","power_noise","witch_house","ccm","christian_metal","christian_pop","christian_rap","christian_rock","gospel","qawwali","southern_gospel","march","j_rock","j_synth","j_ska","j_punk","bebop","big_band","blue_note","cool","crossover_jazz","dixieland","ethio_jazz","fusion","gypsy_jazz","hard_bop","mainstream_jazz","latin_jazz","ragtime","smooth_jazz","trad_jazz","third_stream","jazz_funk","free_jazz","modal_jazz","k_pop","karaoke","kayokyoku","latin","argentine_tango","bachata","baithak_gana","bolero","bossa_nova","brazilian","axé","brazilian_rock","brega","choro","forró","frevo","funk_carioca","lambada","maracatu","pagode","samba","samba_rock","tecnobrega","tropicalia","zouk_lambada","chicha","criolla","cumbia","huayno","mariachi","merengue_típico","nuevo_flamenco","pop_latino","portuguese_fado","punta","punta_rock","ranchera","raíces","raison","soca","son","tejano","timba","twoubadou","zouk","speed_metal","power_metal","black_metall","pagan_metal","viking_metal","folk_metal","symphonic_metal","gothic_metal","glam_metal","hair_metal","doom_metal","groove_metal","modern_metal","post_metal","sludge","djent","drone","kawaii_metal","pirate_metal","nu_metal","math_metal","crossover","grindcore","deathcore","post_hardcore","mathcore","new_age","environmental","healing","meditation","nature","relaxation","travel","arab_pop","britpop","bubblegum_pop","chamber_pop","chanson","europop","austropop","jangle_pop","popera","balkan_pop","latin_pop","laïkó","nederpop","russian_pop","dance_pop","dream_pop","electro_pop","iranian_pop","latin_ballad","levenslied","mexican_pop","motorpop","new_romanticism","orchestral_pop","pop_rap","pop_punk","power_pop","psychedelic_pop","schlager","soft_rock","sophisti_pop","space_age_pop","sunshine_pop","surf_pop","teen_pop","turkish_pop","vispop","wonky_pop","post_disco","boogie","disco_house","dream_house","space_house","japanese_house","disco","doo_wop","modern_soul","motown","neo_soul","northern_soul","quiet_storm","southern_soul","reggae","2_tone","dancehall","dub","roots_reggae","reggae_fusion","spanish_reggae","reggae_110","reggae_bultrón","romantic_flow","lovers_rock","raggamuffin","ragga","ska","rocksteady","math_rock","metal_core","acid_rock","afro_punk","anatolian_rock","arena_rock","art_rock","cock_rock","glam_rock","grind_core","noise_rock","jam_bands","post_punk","rock_&_roll","rockabilly","roots_rock","southern_rock","spazzcore","stoner_metal","surf","tex_mex","time_lord_rock","trock","folk_rock","love_song","new_acoustic","foreign_cinema","musicals","original_score","tv_soundtrack","chicano","conjunto","new_mex","vocal","a_cappella","barbershop","cantique","gregorian_chant","standards","traditional_pop","vocal_jazz","vocal_pop","world","afro_beat","afro_pop","apala","benga","bikutsi","bongo_flava","cape_jazz","chimurenga","coupé_décalé","fuji_music","genge","highlife","hiplife","isicathamiya","jit","jùjú","kapuka","kizomba","kuduro","kwaito","kwela","makossa","maloya","marrabenta","mbalax","mbaqanga","mbube","morna","museve","palm_wine","raï","sakara","sega","seggae","semba","soukous","taarab","zouglou","asia","anison","c_pop","cantopop","fann_at_tanbura","fijiri","japanese_pop","khaliji","kayōkyoku","korean_pop","liwa","mandopop","onkyokei","taiwanese_pop","sawt","australia","cajun","calypso","caribbean","chutney","chutney_soca","compas","mambo","merengue","méringue","carnatic","celtic","celtic_folk","dangdut","europe","france","hawaii","japan","klezmer","middle_east","north_america","ode","piphat","polka","baila","bhangra","bhojpuri","filmi","indian_pop","hindustani","indian_ghazal","lavani","luk_thung","luk_krung","manila_sound","morlam","pinoy_pop","pop_sunda","ragini","thai_pop","worldbeat"]
netwrk = pylast.LastFMNetwork(api_key=Config.LASTFM_API_KEY, api_secret=Config.LASTFM_SECRET, username=Config.LASTFM_USERNAME, password_hash=pylast.md5(Config.LASTFM_PASSWORD))
igr = "https://i.imgur.com/"
pcurl = [f"{igr}l772pcA.png", f"{igr}KehK98D.png", f"{igr}LuwSKeO.png", f"{igr}EZ1S9cJ.png", f"{igr}g20T1of.png", f"{igr}iXzXaDp.png"]
welp = ["https:\/\/lastfm.freetls.fastly.net\/i\/u\/300x300\/2a96cbd8b46e442fc41c2b86b821562f.png","https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png","",]

def tglst():
    return tglst_

def auth_():
    return netwrk

def ri(img):
    return rand_array(pcurl) if img in welp else img

async def user():
    data = await get_collection("CONFIGS").find_one({"_id": "SHOW_LASTFM"})
    user_ = await userge.get_me()
    return f"[{user_.first_name}]({du}{Config.LASTFM_USERNAME})" if data and data["on"] == "Show" else f"{user_.first_name}"

async def resp(params: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://ws.audioscrobbler.com/2.0", params=params) as resp:
            status_code = resp.status
            json_ = await resp.json()
        await session.close()
    return status_code, json_

async def recs(query, typ, lim):
    params = {"method": f"user.get{typ}", "user": query, "limit": lim, "api_key": Config.LASTFM_API_KEY, "format": "json"}
    res = await resp(params)
    return res

async def info(wo, query, art, tr):
    params = {"method": f"{wo}.getInfo", "api_key": Config.LASTFM_API_KEY, "format": "json"}
    if wo=="user":
        params['user']=query
    else:
        params['track'], params['artist']=tr, art
        if query!="":
            params['user']=query
    res = await resp(params)
    return res
