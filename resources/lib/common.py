import json
# import datetime
import urllib,urllib2
import xbmc,xbmcplugin,xbmcgui
import requests
from xml.dom.minidom import parseString

import vars
# from utils import *

# def getFanartImage():
#     # get the feed url
#     feed_url = "http://smb.cdnak.neulion.com/fs/nba/feeds/common/dl.js"
#     req = urllib2.Request(feed_url, None);
#     response = str(urllib2.urlopen(req).read())

#     try:
#         # Parse
#         js = json.loads(response[response.find("{"):])
#         dl = js["dl"]

#         # for now only chose the first fanart
#         first_id = dl[0]["id"]
#         fanart_image = ("http://smb.cdnllnwnl.neulion.com/u/nba/nba/thumbs/dl/%s_pc.jpg" % first_id)
#         vars.settings.setSetting("fanart_image", fanart_image)
#     except:
#         print "Failed to parse the dl output!!!"
#         return ''

# def getDate( default= '', heading='Please enter date (YYYY/MM/DD)', hidden=False ):
#     now = datetime.datetime.now()
#     default = "%04d" % now.year + '/' + "%02d" % now.month + '/' + "%02d" % now.day
#     keyboard = xbmc.Keyboard( default, heading, hidden )
#     keyboard.doModal()
#     ret = datetime.date.today()
#     if ( keyboard.isConfirmed() ):
#         sDate = unicode( keyboard.getText(), "utf-8" )
#         temp = sDate.split("/")
#         ret = datetime.date(int(temp[0]),  int(temp[1]), int(temp[2]))
#     return ret

class NBAServiceError(Exception):
    def __init__(self, message, cause=None):

        super(NBAServiceError, self).__init__(message)

        self.cause = cause

class NBAServiceBadLogin(NBAServiceError):
    def __init__(self, message, username, password, cause=None):

        super(NBAServiceBadLogin, self).__init__(message + (' for user "%s"' % username), cause)

        self.username = username
        self.password = password

def login():
    username = vars.settings.getSetting(id="username")
    password = vars.settings.getSetting(id="password")
    if not username or not password:
        raise NBAServiceBadLogin('Bad login information', username, password)

    vars.session = requests.Session()
    failsafe = True
    headers = {
        'User-Agent': 'iPad' if failsafe
            else "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
    }
    vars.session.headers.update(headers)

    # Login
    url = 'https://watch.nba.com/nba/secure/login'
    creds = {'username': username, 'password': password}

    try:
        r = vars.session.get(url, params=creds)
        r.raise_for_status()
        content = r.text
    except requests.exceptions.HTTPError as e:
        print 'NBA League Pass - Error logging in: %s' % str(e)
        raise NBAServiceError('Logging in to NBA service', e)

    # Check the response xml
    xml = parseString(str(content))
    if xml.getElementsByTagName("code")[0].firstChild.nodeValue == "loginlocked":
        raise NBAServiceBadLogin('Login locked', username, password)

    return vars.session
