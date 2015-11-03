import json
import time
import requests

import urllib,urllib2
import xbmc,xbmcplugin,xbmcgui
from xml.dom.minidom import parseString
import os, re
import sys

from utils import *
from common import *
import vars

from team import Team
from game import Game
from neulion import neulion as NeuLion

def generateGameItem(game, title):
    image = os.path.join(vars.media_dir, 'images', game.visitors.id, 'logo.png')
    fanart = os.path.join(vars.media_dir, 'images', game.homeTeam.id, 'fanart.jpg')
    item = xbmcgui.ListItem(title)
    item.setArt({'thumb': image, 'fanart': fanart})
    item.setIconImage(image)

    return item

class NBAGameTimeError(Exception):
    def __init__(self, message, cause=None):

        super(NBAGameTimeError, self).__init__(message)

        self.cause = cause

class GameTime():
    def __init__(self):
        self.plugin = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]
        self.pluginBase = sys.argv[0]

        self.session = requests.Session()

        self.myTeam = Team(name=vars.settings.getSetting(id="my_team"))

    def menu(self):
        # My Team
        if self.myTeam:
            # My Team
            image = os.path.join(vars.media_dir, 'images', self.myTeam.id, 'logo.png')
            fanart = os.path.join(vars.media_dir, 'images', self.myTeam.id, 'fanart.jpg')

            item = xbmcgui.ListItem('My '+self.myTeam.name)
            item.setArt({'thumb': image, 'fanart': fanart})
            item.setIconImage(image)

            xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/myteam', listitem=item, isFolder=True)

        # LIVE Games
        if isLiveUsable():
            image = os.path.join(vars.media_dir, 'images', 'nba_tv.png')
            item = xbmcgui.ListItem('LIVE Games')
            item.setArt({'thumb': image, 'fanart': vars.fanart_image})
            item.setIconImage(image)
            item.setInfo('video', {'genre': 'Sport', 'year': '2015', 'playcount': 0, 'tvshowtitle': 'NBA TV Live'})
            item.setProperty('AspectRatio', '16 : 9')

            xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/livegames', listitem=item, isFolder=True)

        # Days Top Picks
        image = os.path.join(vars.home_dir, 'icon.png')
        item = xbmcgui.ListItem('Days Top Picks')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/toppicks', listitem=item, isFolder=True)

        # Past 24 Hours
        image = os.path.join(vars.home_dir, 'icon.png')
        item = xbmcgui.ListItem('Past 24 Hours')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/past24hours', listitem=item, isFolder=True)

        # Past 7 Days
        image = os.path.join(vars.home_dir, 'icon.png')
        item = xbmcgui.ListItem('Past 7 Days')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/past7days', listitem=item, isFolder=True)

        now = date.today()
        year = now.year
        if now.month < 10:
            year -= 1

        seasons = range(year-1, 2012-1, -1)

        # 2014 - 2015 Season Archive
        image = os.path.join(vars.home_dir, 'icon.png')
        item = xbmcgui.ListItem('Current Season')
        item.setArt({'thumb': image, 'fanart': vars.fanart_image})
        item.setIconImage(image)

        xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/season/%d-%d' % (year, year+1), listitem=item, isFolder=True)

        for season in seasons:
            image = os.path.join(vars.home_dir, 'icon.png')
            item = xbmcgui.ListItem('%d - %d Season' % (season, season+1))
            item.setArt({'thumb': image, 'fanart': vars.fanart_image})
            item.setIconImage(image)

            xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/season/%d-%d' % (season, season+1), listitem=item, isFolder=True)

        xbmcplugin.endOfDirectory(self.handle)

        # Select first item in list
        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        controlList = window.getFocus()
        controlList.selectItem(1)
        self.firstRender = False

    def myteam(self):
        now = estNow()
        monday = toMondayOfWeek(now)

        games = []
        games.extend(NeuLion.getGames(subtractWeek(monday)))
        games.extend(NeuLion.getGames(monday))
        games.extend(NeuLion.getGames(addWeek(monday)))

        games = Game.filterGamesForTeam(self.myTeam, games)
        liveGames = Game.extractLiveGames(now, games)
        pastGames = Game.extractPastGames(now, games)

        # Live Game
        for g in liveGames:
            item = generateGameItem(g, 'LIVE: %s @ %s' % (g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url='%s/play/%s/%s/%s' % (self.pluginBase, g.season, g.weekStart, g.id), listitem=item, isFolder=True)

        # Past 7 days of games
        for g in pastGames:
            print 'grrr', self.handle, self.plugin
            item = generateGameItem(g, 'REPLAY [%s]: %s @ %s' % (gameDateToString(g.startTime), g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url='%s/play/%s/%s/%s' % (self.pluginBase, g.season, g.weekStart, g.id), listitem=item)

        # Next 7 days of upcoming games as placeholders
        for g in games:
            item = generateGameItem(g, 'FUTURE [%s]: %s @ %s' % (gameTimeToString(g.scheduledTime), g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url='%s/play/%s/%s/%s' % (self.pluginBase, g.season, g.weekStart, g.id), listitem=item)

        xbmcplugin.endOfDirectory(self.handle)

    def livegames(self):
        now = estNow()
        tomorrow = addDay(now)
        monday = toMondayOfWeek(now)

        games = []
        games.extend(NeuLion.getGames(monday))

        liveGames = Game.extractLiveGames(now, games)
        upcoming = []
        for g in games:
            if g.scheduledTime > now and g.scheduledTime < tomorrow:
                upcoming.append(g)

        # Live Game
        for g in liveGames:
            item = generateGameItem(g, 'LIVE: %s @ %s' % (g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url='%s/play/%s/%s/%s' % (self.pluginBase, g.season, g.weekStart, g.id), listitem=item)

        # Next 7 days of upcoming games as placeholders
        for g in upcoming:
            item = generateGameItem(g, 'FUTURE [%s]: %s @ %s' % (gameTimeToString(g.scheduledTime), g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url='', listitem=item)


        xbmcplugin.endOfDirectory(self.handle)

    def toppicks(self):
        now = myNow()
        monday = toMondayOfWeek(now)

        games = []
        games.extend(NeuLion.getGames(monday))

        games = Game.extractPastGames(now, games)
        topGames = Game.extractTopPicks(now, games)

        print topGames

        # Live Game
        for g in topGames:
            item = generateGameItem(g, 'REPLAY [%s]: %s @ %s' % (gameDateToString(g.startTime), g.visitors.name, g.homeTeam.name))
            xbmcplugin.addDirectoryItem(handle=self.handle, url=self.plugin+'/playLiveTV', listitem=item, isFolder=True)

        xbmcplugin.endOfDirectory(self.handle)

    def execute(self):
        print self.plugin
        match = re.search('(plugin://[^/]+/gametime)/([^/]+)(/([^/]+)/([^/]+)/([^/]+))?$', self.plugin)

        if match:
            self.pluginBase = match.group(1)
            print match.lastgroup, match.group(4), match.group(5), match.group(6)
            if match.group(2) == 'myteam':
                self.myteam()
            elif match.group(2) == 'livegames':
                self.livegames()
            elif match.group(2) == 'toppicks':
                self.toppicks()
            elif match.group(2) == 'past24hours':
                NBATVLive.execute()
            elif match.group(2) == 'past7days':
                playLiveTV()
            elif match.group(2) == 'season':
                NBATVLive.execute()
            elif match.group(2) == 'play' and match.lastindex == 3:
                g = NeuLion.getGame(match.group(4), match.group(5), match.group(6))
                print g
                video_url = getGameFeedUrl(g)
                if not video_url:
                    log("no working video_url found error", xbmc.LOGDEBUG)

                title = '%s @ %s' % (g.visitors.name, g.homeTeam.name)
                if int(g.status) == 1:
                  title = 'LIVE: %s' % title
                else:
                  title = 'REPLAY: %s' % title

                item = xbmcgui.ListItem(label=title)
                item.setInfo('video', {'Title': title, 'Genre': 'Sports'})

                xbmcplugin.setResolvedUrl(handle=self.handle, succeeded=True, listitem=item)
                xbmc.Player().play(video_url, item)

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

gametime = GameTime()

def getGameFeedUrl(game, feedPreference='home'):
    if not vars.session:
        login()

    failsafe = True;

    url = 'http://watch.nba.com/service/publishpoint'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'iPad' if game.status == 1
            else "AppleCoreMedia/1.0.0.8C148a (iPad; U; CPU OS 6_2_1 like Mac OS X; en_us)",
    }

    body = {
        'extid': game.id,
        'type': 'game',
        'plid': vars.player_id,
        'gt': '1',
        'gs': game.status,
        'format': 'xml'
    }

    log("nba game time: the body for publishpoint request are: %s" % str(body), xbmc.LOGDEBUG)
    print "nba game time: the body for publishpoint request are: %s" % str(body)

    try:
        import logging
        logging.basicConfig()
        currentLevel = logging.getLogger().getEffectiveLevel()
        # if currentLevel == logging.DEBUG:
        from six.moves import http_client
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        r = vars.session.post(url, data=body, headers=headers)
        r.raise_for_status()
        content = r.text
    except requests.exceptions.HTTPError as e:
        log("Retrieving game url (%s) failed with content: %s" % (str(game.id), str(r.text)), xbmc.LOGDEBUG)
        raise NBAGameTimeError('Retreiving game url data: "%s"' % r.text, e)
        raise e

    xml = parseString(str(content))
    m3u8Url = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
    log(m3u8Url, xbmc.LOGDEBUG)
    print m3u8Url

    selected_video_url = getGameUrlWithBitrate(m3u8Url)

    if selected_video_url:
        log("the url of video %s is %s" % (game.id, selected_video_url), xbmc.LOGDEBUG)
        print "the url of video %s is %s" % (game.id, selected_video_url)

    return selected_video_url

def getGameUrl(video_id, video_type='archive', video_ishomefeed=True):
    # # video_type could be archive, live, condensed or oldseason
    # if video_type not in ["live", "archive", "condensed"]:
    #     video_type = "archive"

    # url = 'http://watch.nba.com/nba/servlets/publishpoint'
    # headers = {
    #     'Cookie': vars.cookies,
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'User-Agent': 'iPad' if video_type == "live"
    #         else "AppleCoreMedia/1.0.0.8C148a (iPad; U; CPU OS 6_2_1 like Mac OS X; en_us)",
    # }
    # body = {
    #     'id': str(video_id),
    #     'gt': video_type + ("away" if not video_ishomefeed else ""),
    #     'type': 'game',
    #     'plid': vars.player_id,
    #     'nt': '1'
    # }
    # if video_type != "live":
    #     body['format'] = 'xml'
    # body = urllib.urlencode(body)

    # log("the body of publishpoint request is: %s" % body, xbmc.LOGDEBUG)

    # try:
    #     request = urllib2.Request(url, body, headers)
    #     response = urllib2.urlopen(request)
    #     content = response.read()
    # except urllib2.HTTPError as e:
    #     log("Failed to get video url. The url was %s, the content was %s" % (url, e.read()))
    #     xbmc.executebuiltin('Notification(NBA League Pass,Failed to get a video URL. Are you logged in?,5000,)')
    #     return ''

    if not vars.session:
        login()

    failsafe = True;
    gameStatus = "http://smb.cdnak.neulion.com/fs/nba/feeds_s2012/stats/%d/pbp/%d.js?t=%d" % (year, gameid, timestampmillis)

    # video_type could be archive, live, condensed or oldseason
    if video_type not in ["live", "archive", "condensed"]:
        video_type = "archive"

    url = 'http://watch.nba.com/service/publishpoint'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'iPad' if video_type == "live"
            else "AppleCoreMedia/1.0.0.8C148a (iPad; U; CPU OS 6_2_1 like Mac OS X; en_us)",
    }
    body = {
        'extid': str(video_id),
        'type': 'game',
        'plid': vars.player_id,
        'gt': video_type + ("away" if not video_ishomefeed else ""),
        'nt': '1'
        # 'gt': '1',
        # 'gs': '1'
    }
    if video_type != "live":
        body['format'] = 'xml'

    log("nba game time: the body for publishpoint request are: %s" % str(body), xbmc.LOGDEBUG)
    print "nba game time: the body for publishpoint request are: %s" % str(body)

    try:
        import logging
        logging.basicConfig()
        currentLevel = logging.getLogger().getEffectiveLevel()
        # if currentLevel == logging.DEBUG:
        from six.moves import http_client
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        r = vars.session.post(url, data=body, headers=headers)
        r.raise_for_status()
        content = r.text
    except requests.exceptions.HTTPError as e:
        log("Retrieving game url (%s) failed with content: %s" % (str(video_id), str(r.text)), xbmc.LOGDEBUG)
        raise NBAGameTimeError('Retreiving game url data: "%s"' % r.text, e)
        raise e

    print content

    xml = parseString(str(content))
    url = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
    log(url, xbmc.LOGDEBUG)

    selected_video_url = ''
    if video_type == "live":
        # transform the url
        match = re.search('http://([^:]+)/([^?]+?)\?(.+)$', url)
        domain = match.group(1)
        arguments = match.group(2)
        querystring = match.group(3)

        livecookies = "nlqptid=%s" % (querystring)
        livecookiesencoded = urllib.quote(livecookies)

        log("live cookie: %s %s" % (querystring, livecookies), xbmc.LOGDEBUG)

        url = "http://%s/%s?%s" % (domain, arguments, querystring)
        url = getGameUrlWithBitrate(url, is_live = True)

        selected_video_url = "%s|Cookie=%s" % (url, livecookiesencoded)
    else:
        # Archive and condensed flow: We now work with HLS.
        # The cookies are already in the URL and the server will supply them to ffmpeg later.
        selected_video_url = getGameUrlWithBitrate(url)


    if selected_video_url:
        log("the url of video %s is %s" % (video_id, selected_video_url), xbmc.LOGDEBUG)

    return selected_video_url

def getHighlightGameUrl(video_id):
    url = 'http://watch.nba.com/nba/servlets/publishpoint'
    headers = {
        'Cookie': vars.cookies,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': "AppleCoreMedia/1.0.0.8C148a (iPad; U; CPU OS 6_2_1 like Mac OS X; en_us)",
    }

    body = urllib.urlencode({
        'id': str(video_id),
        'gt': "recapf",
        'type': 'game',
        'plid': vars.player_id,
        'isFlex': "true",
        'bitrate': "1600" # forced bitrate
    })

    log("the body of publishpoint request is: %s" % body, xbmc.LOGDEBUG)

    try:
        request = urllib2.Request(url, body, headers)
        response = urllib2.urlopen(request)
        content = response.read()
    except urllib2.HTTPError:
        return ''

    xml = parseString(str(content))
    url = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue

    # Remove everything after ? otherwise XBMC fails to read the rtpm stream
    url, _,_ = url.partition("?")

    log("highlight video url: %s" % url, xbmc.LOGDEBUG)

    return url

def getGameUrlWithBitrate(url, is_live = False):
    # Force the bitrate by modifying the HLS url and adding the bitrate
    available_bitrates = {
        72060: 4500,
        720: 3000,
        540: 1600,
        432: 1200,
        360: 800,
    }
    target_bitrate = available_bitrates.get(vars.target_video_height, 1600)
    failsafe_bitrate = available_bitrates.get(360)

    regex_pattern = 'whole_([0-9])_ipad'
    regex_replacement_format = r'whole_\1_%s_ipad'
    if is_live:
        regex_pattern = '([a-z]+)_hd_ipad'
        regex_replacement_format = r'\1_hd_%s_ipad'

    #Try the target bitrate
    selected_video_url = re.sub(regex_pattern, regex_replacement_format % target_bitrate, url)
    if urllib.urlopen(selected_video_url).getcode() != 200:
        log("video of height %d not found, trying with height 360" % vars.target_video_height, xbmc.LOGDEBUG)

        #Try the failsafe url (bitrate of 800)
        selected_video_url = re.sub(regex_pattern, regex_replacement_format % failsafe_bitrate, url)
        if urllib.urlopen(selected_video_url).getcode() != 200:
            log("failsafe bitrate video not found, bailing out", xbmc.LOGDEBUG)
            selected_video_url = ""

    return selected_video_url

def addGamesLinks(fromDate = '', video_type = "archive"):
    try:
        schedule = 'http://smb.cdnak.neulion.com/fs/nba/feeds_s2012/schedule/' +fromDate +  '.js?t=' + "%d"  %time.time()
        log('Requesting %s' % schedule, xbmc.LOGDEBUG)

        now_datetime_est = nowEST()

        # http://smb.cdnak.neulion.com/fs/nba/feeds_s2012/schedule/2013/10_7.js?t=1381054350000
        req = urllib2.Request(schedule, None);
        response = str(urllib2.urlopen(req).read())
        js = json.loads(response[response.find("{"):])

        for game in js['games']:
            log(game, xbmc.LOGDEBUG)
            for details in game:
                h = details.get('h', '')
                v = details.get('v', '')
                game_id = details.get('id', '')
                game_start_date_est = details.get('d', '')
                vs = details.get('vs', '')
                hs = details.get('hs', '')
                gs = details.get('gs', '')

                video_has_away_feed = False
                video_details = details.get('video', {})
                video_has_away_feed = video_details.get("af", False)

                # Try to convert start date to datetime
                try:
                    game_start_datetime_est = datetime.datetime.strptime(game_start_date_est, "%Y-%m-%dT%H:%M:%S.%f" )
                except:
                    game_start_datetime_est = datetime.datetime.fromtimestamp(time.mktime(time.strptime(game_start_date_est, "%Y-%m-%dT%H:%M:%S.%f")))

                #Set game start date in the past if python can't parse the date
                #so it doesn't get flagged as live or future game and you can still play it
                #if a video is available
                if type(game_start_datetime_est) is not datetime.datetime:
                    game_start_datetime_est = now_datetime_est + timedelta(-30)

                #guess end date by adding 4 hours to start date
                game_end_datetime_est = game_start_datetime_est + timedelta(hours=4)

                if game_id != '':
                    # Get pretty names for the team names
                    if v.lower() in vars.teams:
                        visitor_name = vars.teams[v.lower()]
                    else:
                        visitor_name = v
                    if h.lower() in vars.teams:
                        host_name = vars.teams[h.lower()]
                    else:
                        host_name = h

                    has_video = "video" in details
                    future_video = game_start_datetime_est > now_datetime_est and \
                        game_start_datetime_est.date() == now_datetime_est.date()
                    live_video = game_start_datetime_est < now_datetime_est < game_end_datetime_est

                    # Create the title
                    name = game_start_datetime_est.strftime("%Y-%m-%d")
                    if video_type == "live":
                        name = toLocalTimezone(game_start_datetime_est).strftime("%Y-%m-%d (at %I:%M %p)")

                    #Add the teams' names and the scores if needed
                    name += ' %s vs %s' % (visitor_name, host_name)
                    if vars.scores == '1' and not future_video:
                        name += ' %s:%s' % (str(vs), str(hs))

                    thumbnail_url = ("http://e1.cdnl3.neulion.com/nba/player-v4/nba/images/teams/%s.png" % h)

                    if video_type == "live":
                        if future_video:
                            name = "UPCOMING: " + name
                        elif live_video:
                            name = "LIVE: " + name

                    add_link = True
                    if video_type == "live" and not (live_video or future_video):
                        add_link = False
                    elif video_type != "live" and (live_video or future_video):
                        add_link = False
                    elif not future_video and not has_video:
                        add_link = False

                    if add_link == True:
                        params = {
                            'video_id': game_id,
                            'video_type': video_type,
                            'video_hasawayfeed': 1 if video_has_away_feed else 0
                        }

                        # Add a directory item that contains home/away/condensed items
                        addListItem(name, url="", mode="gamechoosevideo",
                            iconimage=thumbnail_url, isfolder=True, customparams=params)

    except Exception, e:
        xbmc.executebuiltin('Notification(NBA League Pass,'+str(e)+',5000,)')
        log(str(e))
        pass

def playGame():
    # Authenticate
    if vars.cookies == '':
        vars.cookies = login()

    currentvideo_id = vars.params.get("video_id")
    currentvideo_type  = vars.params.get("video_type")
    currentvideo_ishomefeed = vars.params.get("video_ishomefeed", "1")
    currentvideo_ishomefeed = currentvideo_ishomefeed == "1"

    # Get the video url.
    # Authentication is needed over this point!
    currentvideo_url = getGameUrl(currentvideo_id, currentvideo_type, currentvideo_ishomefeed)
    if currentvideo_url:
        item = xbmcgui.ListItem(path=currentvideo_url)
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
    else:
        xbmc.executebuiltin('Notification(NBA League Pass,Video not found.,5000,)')

def chooseGameVideoMenu():
    currentvideo_id = vars.params.get("video_id")
    currentvideo_type  = vars.params.get("video_type")
    currentvideo_hasawayfeed = vars.params.get("video_hasawayfeed", "0")
    currentvideo_hasawayfeed = currentvideo_hasawayfeed == "1"

    if currentvideo_hasawayfeed:
        # Create the "Home" and "Away" list items
        for ishomefeed in [True, False]:
            listitemname = "Full game, " + ("away feed" if not ishomefeed else "home feed")
            params = {
                'video_id': currentvideo_id,
                'video_type': currentvideo_type,
                'video_ishomefeed': 1 if ishomefeed else 0
            }
            addListItem(listitemname, url="", mode="playgame", iconimage="", customparams=params)
    else:
        #Add a "Home" list item
        params = {
            'video_id': currentvideo_id,
            'video_type': currentvideo_type
        }
        addListItem("Full game", url="", mode="playgame", iconimage="", customparams=params)

    # Create the "Condensed" list item
    if currentvideo_type != "live":
        params = {
            'video_id': currentvideo_id,
            'video_type': 'condensed'
        }
        addListItem("Condensed game", url="", mode="playgame", iconimage="", customparams=params)

        # Get the highlights video if available
        highlights_url = getHighlightGameUrl(currentvideo_id)
        if highlights_url:
            addVideoListItem("Highlights", highlights_url, iconimage="")

    xbmcplugin.endOfDirectory(handle = int(sys.argv[1]) )

def getWeekStarts(time):
    # CDN stores weeks starting on mondays
    day = time.isoweekday()
    return time - timedelta(day-1)

def chooseGameMenu(mode, url, date2Use = None):
    try:
        if mode == "selectdate":
            tday = getDate()
        elif mode == "oldseason":
            tday = date2Use
        else:
            tday = nowEST()
            log("current date (america timezone) is %s" % str(tday), xbmc.LOGDEBUG)

        # parse the video type
        video_type = url

        day = tday.isoweekday()

        # starts on mondays
        tday = tday - timedelta(day -1)
        now = tday
        default = "%04d/%d_%d" % (now.year, now.month, now.day)

        if mode == "lastweek":
            tday = tday - timedelta(7)
            now = tday
            default = "%04d/%d_%d" % (now.year, now.month, now.day)

        addGamesLinks(default, video_type)

        # Can't sort the games list correctly because XBMC treats file items and directory
        # items differently and puts directory first, then file items (home/away feeds
        # require a directory item while only-home-feed games is a file item)
        #xbmcplugin.addSortMethod( handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    except:
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),succeeded=False)
        return None

