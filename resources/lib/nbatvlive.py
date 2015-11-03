import urllib,urllib2
import xbmc,xbmcplugin,xbmcgui,xbmcaddon
from xml.dom.minidom import parseString
import requests

import sys
import os
import re

from common import *
import vars
from utils import *

import logging
logging.basicConfig()
currentLevel = logging.getLogger().getEffectiveLevel()
if currentLevel == logging.DEBUG:
    from six.moves import http_client
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

class NBATVError(Exception):
    def __init__(self, message, cause=None):

        super(NBATVError, self).__init__(message)

        self.cause = cause

class NBATVLive():
    def __init__(self):
        self.plugin = sys.argv[0]
        self.handle = int(sys.argv[1])

    def execute(self):
        if not vars.session:
            login()

        failsafe = True;

        url = 'http://watch.nba.com/nba/servlets/publishpoint'
        params = {
            'id': "0",
            'type': 'channel',
            'plid': vars.player_id,
        }
        if not failsafe:
            params['isFlex'] = 'true'
        else:
            params['nt'] = '1'

        log("nba tv live: the params for publishpoint request are: %s" % str(params), xbmc.LOGDEBUG)

        try:
            r = vars.session.get(url, params=params)
            r.raise_for_status()
            content = r.text
        except requests.exceptions.HTTPError as e:

            log("Login failed with and content: %s" % str(r.text), xbmc.LOGDEBUG)
            raise NBATVError('Retreiving NBA TV Live stream data: "%s"' % r.text, e)
            raise e

        log("nba live tv: publishpoint response was: %s" % content, xbmc.LOGDEBUG)

        # Get the adaptive video url
        xml = parseString(str(content))
        video_temp_url = xml.getElementsByTagName("path")[0].childNodes[0].nodeValue
        log("nba live tv: temp video url is %s" % video_temp_url, xbmc.LOGDEBUG)

        video_url = None

        if re.search('http://([^:]+)/([^?]+?)\?(.+)$', video_temp_url):
            video_url = video_temp_url
        else:
            # Transform the link from adaptive://domain/url?querystring to
            # http://domain/play?url=url&querystring
            match = re.search('adaptive://([^/]+)(/[^?]+)\?(.+)$', video_adaptive_url)
            if match:
                domain = match.group(1)
                path = urllib.quote_plus(str(match.group(2)))
                querystring = match.group(3)
                video_play_url = "http://%s/play?url=%s&%s" % (domain, path, querystring)
                log("nba live tv: play url is %s" % video_play_url, xbmc.LOGDEBUG)

                # Get the video play url (which will return different urls for
                # different bitrates)
                try:
                    request = urllib2.Request(video_play_url, None, {'Cookie': vars.cookies})
                    response = urllib2.urlopen(request)
                    content = response.read()
                except urllib2.HTTPError as e:
                    log("nba live tv: failed getting url: %s %s" % (video_play_url, e.read()))
                    xbmc.executebuiltin('Notification(NBA League Pass,Failed to get a video URL (response != 200),5000,)')
                    return

                if not content:
                    log("nba live tv: empty response from video play url")
                    xbmc.executebuiltin('Notification(NBA League Pass,Failed to get a video URL (response was empty),5000,)')
                    return
                else:
                    log("nba live tv: parsing response: %s" % content, xbmc.LOGDEBUG)

                    # Parse the xml to find different bitrates
                    xml = parseString(str(content))
                    streamdata_list = xml.getElementsByTagName("streamData")
                    video_url = ''
                    for streamdata in streamdata_list:
                        video_height = streamdata.getElementsByTagName("video")[0].attributes["height"].value

                        if int(video_height) == vars.target_video_height:
                            selected_video_path = streamdata.attributes["url"].value
                            http_servers = streamdata.getElementsByTagName("httpserver")

                            for http_server in http_servers:
                                server_name = http_server.attributes["name"].value
                                server_port = http_server.attributes["port"].value

                                # Construct the video url directly in m3u8
                                m3u8_video_url = "http://%s:%s%s.m3u8" % (server_name, server_port, selected_video_path)

                                # Test if the video is actually available. If it is not available go to the next server.
                                if urllib.urlopen(m3u8_video_url).getcode() == 200:
                                    video_url = m3u8_video_url

                                    # Get the cookies from the xml tag <encryption>
                                    video_cookies = streamdata.getElementsByTagName("encryption")[0].attributes['token'].value
                                    video_cookies = video_cookies.replace(';', '; ')
                                    video_cookies_encoded = urllib.quote(video_cookies)
                                    log("nba live tv: live cookie: %s" % video_cookies, xbmc.LOGDEBUG)
                                    break

                                log("no working url found for this server, moving to the next", xbmc.LOGDEBUG)

                            # break from the video quality loop
                            break

                # Add the cookies in the format "videourl|Cookie=[cookies]""
                video_url = "%s?%s|Cookie=%s" % (video_url, querystring, video_cookies_encoded)

        if not video_url:
            log("no working video_url found error", xbmc.LOGDEBUG)

        image = os.path.join(vars.media_dir, 'images', 'nba_tv', 'logo.png')
        fanart = os.path.join(vars.media_dir, 'images', 'nba_tv', 'fanart.jpg')
        item = xbmcgui.ListItem('NBA TV Live')
        item.setArt({'thumb': image, 'fanart': fanart})
        item.setIconImage(image)
        item.setInfo('video', {'genre': 'Sports', 'year': '2015', 'playcount': 0, 'tvshowtitle': 'NBA TV Live'})
        item.setProperty('AspectRatio', '16 : 9')

        xbmc.Player().play(video_url, item)

nbatvlive = NBATVLive()
