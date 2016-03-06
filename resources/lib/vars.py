import xbmc,xbmcplugin,xbmcgui,xbmcaddon
import os,binascii

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

__addon_name__ = "NBA League Pass"

# global variables
addonName = 'plugin.video.russ-ba'
settings = xbmcaddon.Addon(id=addonName)
scores = settings.getSetting(id="scores")
debug = settings.getSetting(id="debug")
device_emulation = settings.getSetting(id="device_emulation")
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
use_local_timezone = settings.getSetting(id="local_timezone") == "0"

# map the quality_id to a video height
# Ex: 720p
quality_id = settings.getSetting( id="quality_id")
video_heights_per_quality = [72060, 720, 540, 432, 360]
target_video_height = video_heights_per_quality[int(quality_id)]

cache = StorageServer.StorageServer("nbaleaguepass", 1)
cache.table_name = "nbaleaguepass"

# Delete the video urls cached if the video quality setting has changed
if cache.get("target_video_height") != str(target_video_height):
    cache.delete("video_%")
    cache.set("target_video_height", str(target_video_height))
    print "deleting video url cache"

session = None
player_id = binascii.b2a_hex(os.urandom(16))
home_dir = os.path.join(
    xbmc.translatePath("special://home/" ),
    "addons", "plugin.video.russ-ba"
)
media_dir = os.path.join(home_dir, 'resources', 'media')
# # the default fanart image
fanart_image = os.path.join(home_dir, "fanart.jpg")
settings.setSetting('fanart_image', fanart_image)
# setting_fanart_image = settings.getSetting("fanart_image")
# if setting_fanart_image != '':
#     fanart_image = setting_fanart_image

# print "russ-ba: media dir: %s, fanart_image: %s => %s" % (media_dir, fanart_image, setting_fanart_image)
print "russ-ba: media dir: %s, fanart_image: %s" % (media_dir, settings.getSetting("fanart_image"))

teams = {
    'por': 'Blazers',
    'mil': 'Bucks',
    'chi': 'Bulls',
    'cle': 'Cavaliers',
    'bos': 'Celtics',
    'lac': 'Clippers',
    'mem': 'Grizzlies',
    'atl': 'Hawks',
    'mia': 'Heat',
    'cha': 'Hornets',
    'uta': 'Jazz',
    'sac': 'Kings',
    'nyk': 'Knicks',
    'lal': 'Lakers',
    'orl': 'Magic',
    'dal': 'Mavericks',
    'bkn': 'Nets',
    'den': 'Nuggets',
    'ind': 'Pacers',
    'nop': 'Pelicans',
    'det': 'Pistons',
    'tor': 'Raptors',
    'hou': 'Rockets',
    'phi': 'Sixers',
    'sas': 'Spurs',
    'phx': 'Suns',
    'okc': 'Thunder',
    'min': 'Timberwolves',
    'gsw': 'Warriors',
    'was': 'Wizards',
    # non nba
    "fbu" : "Fenerbahce",
    "ubb" : "Bilbao",
    'mos' : "UCKA Moscow",
    'mac' : "Maccabi Haifa",
}
