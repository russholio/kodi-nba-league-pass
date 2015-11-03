# from datetime import date
# from datetime import timedelta
import urllib
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
import sys

from resources.lib.utils import *
from resources.lib.gametime import gametime as GameTime
from resources.lib.common import *
from resources.lib.videos import *
from resources.lib.nbatvlive import nbatvlive as NBATVLive
import resources.lib.vars

import os, re

log("Chosen quality_id %s and target_video_height %d" % (vars.quality_id, vars.target_video_height))

class LeaguePass:
    def __init__(self):
        self.plugin = sys.argv[0]
        self.handle = int(sys.argv[1])
        xbmcplugin.setPluginFanart(handle=self.handle, image=vars.fanart_image, color1='0xFF000033', color2='0x00FF0077', color3='0x0000FFDD')
        if not vars.settings.getSetting('username') or not vars.settings.getSetting('password'):
            xbmcaddon.Addon(vars.addonName).openSettings()

    def menu(self):
        # Game Time
        image = os.path.join(vars.media_dir, 'images', 'nba_espn.png')
        item = xbmcgui.ListItem('Game Time')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'gametime', listitem=item, isFolder=True)

        # NBA TV Live
        if isLiveUsable():
            image = os.path.join(vars.media_dir, 'images', 'nba_tv', 'logo.png')
            fanart = os.path.join(vars.media_dir, 'images', 'nba_tv', 'fanart.jpg')
            item = xbmcgui.ListItem('NBA TV Live')
            item.setArt({'thumb': image, 'fanart': fanart})
            item.setIconImage(image)
            item.setInfo('video', {'genre': 'Sport', 'year': '2015', 'playcount': 0, 'tvshowtitle': 'NBA TV Live'})
            item.setProperty('AspectRatio', '16 : 9')

            xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'nbatvlive', listitem=item)

        # Videos
        image = os.path.join(vars.home_dir, 'icon.png')
        item = xbmcgui.ListItem('Videos')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'videos', listitem=item, isFolder=True)

        xbmcplugin.endOfDirectory(self.handle)

        # Select first item in list
        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        controlList = window.getFocus()
        controlList.selectItem(1)
        self.firstRender = False

    def execute(self):
        try:
            match = re.search('plugin://[^/]+/([^/]+)', self.plugin)

            if match:
                if match.group(1) == 'gametime':
                    GameTime.execute()
                elif match.group(1) == 'nbatvlive':
                    NBATVLive.execute()
                elif match.group(1) == 'videos':
                    playLiveTV()

                # elif mode == "archive":
                #     archiveMenu()
                # elif mode == "playgame":
                #     playGame()
                # elif mode == "gamechoosevideo":
                #     chooseGameVideoMenu()
                # elif mode == "oldseason":
                #     previousSeasonMenu()
                # elif mode == "live":
                #     liveMenu()
                # elif mode.startswith("video"):
                #     if mode == "videoplay":
                #         videoPlay()
                #     elif mode == "videodate":
                #         videoMenu()
                #     else:
                #         videoDateMenu()
                # else:
                #     chooseGameMenu(mode, url)
            else:
                self.menu()

        except NBAServiceError as e:
            xbmcgui.Dialog().notification(heading='NBA League Pass', message='Error: %s' % e, icon=xbmcgui.NOTIFICATION_WARNING, time=7000, sound=True)
            if (isinstance(e, NBAServiceBadLogin)):
                xbmcaddon.Addon(vars.addonName).openSettings()

leaguepass = LeaguePass()
leaguepass.execute()

def archiveMenu():
    addListItem('This week', "archive", 'thisweek' ,'', True)
    addListItem('Last week' , "archive", 'lastweek','', True)
    addListItem('Select date' , "archive", 'selectdate','', True)

    # Dynamic previous season, so I don't have to update this every time!
    now = date.today()
    is_season_active = False
    is_season_first_year = False
    if now.month >= 10 and date(now.year, 10, 28) < now < date(now.year+1, 6, 30):
        is_season_active = True
        is_season_first_year = True
    elif now.month < 10 and date(now.year-1, 10, 28) < now < date(now.year, 6, 30):
        is_season_active = True

    current_year = now.year
    if is_season_active and not is_season_first_year:
        current_year -= 1

    # Available previous seasons starts from 2012 (2012-1 because range() doesn't include the last year)
    for year in range(current_year-1, 2012-1, -1):
        params = {
            'oldseasonyear': year
        }
        addListItem('%d-%d season' % (year, year+1), url="", mode='oldseason',
            iconimage='', isfolder=True, customparams=params)

def liveMenu():
    chooseGameMenu('', 'live')


def previousSeasonMenu():
    season_year = vars.params.get("oldseasonyear")
    season_year = int(season_year)
    start_date = date(season_year, 10, 30)

    # Get the games for 36 weeks
    for week in range(1, 36):
        chooseGameMenu(mode, url, start_date)
        start_date = start_date + timedelta(7)


# try:
#     plugin = sys.argv[0]
#     params = getParams()
#     print str(params)
#     url = urllib.unquote_plus(params.get("url", ""))
#     mode = params.get("mode", None)
#     doit = True

#     match = re.search('plugin://[^/]+/(.+)$', plugin)

#     if match:
#         if match.group(1) == 'gametime':
#             playLiveTV()
#         elif match.group(1) == 'nbatvlive':
#             playLiveTV()
#         elif match.group(1) == 'videos':
#             playLiveTV()
#     else:
#         # Save the params in 'vars' to retrieve it in the functions
#         vars.params = params;

#         if mode == None:
#             # getFanartImage()
#             mainMenu()
#             doit = False
#         elif mode == "archive":
#             archiveMenu()
#         elif mode == "playgame":
#             playGame()
#         elif mode == "gamechoosevideo":
#             chooseGameVideoMenu()
#         elif mode == "oldseason":
#             previousSeasonMenu()
#         elif mode == "live":
#             liveMenu()
#         elif mode.startswith("video"):
#             if mode == "videoplay":
#                 videoPlay()
#             elif mode == "videodate":
#                 videoMenu()
#             else:
#                 videoDateMenu()
#         else:
#             chooseGameMenu(mode, url)

#         if doit:
#             xbmcplugin.endOfDirectory(int(sys.argv[1]))
# except NBAServiceError as e:
#     xbmcgui.Dialog().notification(heading='NBA League Pass', message='Error: %s' % e.message, icon=xbmcgui.NOTIFICATION_WARNING, time=7000, sound=True)
