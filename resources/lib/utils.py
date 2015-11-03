import xbmc
import json
# import xbmcplugin,xbmcgui,xbmcaddon
# import urllib,datetime,json,sys,pytz
# from dateutil.tz import tzlocal

import vars

from datetime import *
from dateutil.tz import *
import time
from dateutil import parser
from pytz import timezone
import pytz

# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('time')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('dateshort')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('datelong')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('meridiem')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('tempunit')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.getRegion('speedunit')
# print '\n\n\n\n%s\n\n\n\n\n' % xbmc.__date__

dateformat = xbmc.getRegion('dateshort')
timeformat = xbmc.getRegion('time')
datetimeformat = '%s %s' % (dateformat, timeformat)

utc = pytz.utc
eastern = timezone('US/Eastern')
local = pytz.build_tzinfo('localtime', open('/etc/localtime', 'rb'))

def myNow():
    if hasattr(myNow, 'datetime'):
        return myNow.datetime

    myNow.datetime = datetime.now(local)
    # myNow.datetime = parser.parse('2015-04-26T00:09:25-04:00')
    return myNow.datetime

def estNow():
    if hasattr(estNow, 'datetime'):
        return estNow.datetime

    estNow.datetime = datetime.now(eastern)
    return estNow.datetime

def gmtTime(isoTime):
    return eastern.localize(parser.parse(isoTime))

def gameTime(isoTime):
    return utc.localize(parser.parse(isoTime))

def toMondayOfWeek(dt):
    return dt - timedelta(dt.isoweekday()-1)

def addWeek(dt):
    return dt + timedelta(7)

def subtractWeek(dt):
    return dt - timedelta(7)

def addDay(dt):
    return dt + timedelta(1)

def subtractDay(dt):
    return dt - timedelta(1)

def gameDateToString(datetime, convertTolocal=True):
    """Return the date of the datetime provided"""
    dt = dateime if not convertTolocal else datetime.astimezone(local)
    return dt.strftime(dateformat);

def gameTimeToString(datetime, convertTolocal=True):
    """Return the time of the datetime provided"""
    dt = dateime if not convertTolocal else datetime.astimezone(local)
    return dt.strftime(datetimeformat);

# #Get the current date and time in EST timezone
# def nowEST():
#     if hasattr(nowEST, "datetime"):
#         return nowEST.datetime

#     #Convert UTC to EST datetime
#     timezone = pytz.timezone('America/New_York')
#     utc_datetime = datetime.datetime.utcnow()
#     est_datetime = utc_datetime + timezone.utcoffset(utc_datetime)
#     log("UTC datetime: %s" % utc_datetime)
#     log("EST datetime: %s" % est_datetime)

#     #Save the result to a static variable
#     nowEST.datetime = est_datetime

#     return est_datetime

# #Returns a datetime in the local timezone
# #Thanks: http://stackoverflow.com/a/8328904/2265500
# def toLocalTimezone(date):
#     #Check settings
#     if not vars.use_local_timezone:
#         return date

#     #Pick the first timezone name found
#     local_timezone = tzlocal()

#     #Get the NBA league pass timezone (EST)
#     est_timezone = pytz.timezone('America/New_York')

#     #Localize the date to include the offset, then convert to local timezone
#     return est_timezone.localize(date).astimezone(local_timezone)

def isLiveUsable():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    version_installed = []
    if json_query.has_key('result') and json_query['result'].has_key('version'):
        version_installed  = json_query['result']['version']
        log("Version installed %s" %version_installed, xbmc.LOGDEBUG)

    return version_installed and version_installed['major'] >= 13

def log(txt, severity=xbmc.LOGINFO):
    if severity == xbmc.LOGDEBUG and not vars.debug:
        pass
    else:
        try:
            message = ('##### %s: %s' % (vars.__addon_name__,txt) )
            xbmc.log(msg=message, level=severity)
        except UnicodeEncodeError:
            message = ('##### %s: UnicodeEncodeError' %vars.__addon_name__)
            xbmc.log(msg=message, level=xbmc.LOGWARNING)

# def getParams():
#     param={}
#     paramstring=sys.argv[2]
#     if len(paramstring)>=2:
#         params=sys.argv[2]
#         cleanedparams=params.replace('?','')
#         if (params[len(params)-1]=='/'):
#             params=params[0:len(params)-2]
#         pairsofparams=cleanedparams.split('&')
#         param={}
#         for i in range(len(pairsofparams)):
#             splitparams={}
#             splitparams=pairsofparams[i].split('=')
#             if (len(splitparams))==2:
#                 param[splitparams[0]]=splitparams[1]
#     return param

# def addVideoListItem(name, url, iconimage):
#     return addListItem(name,url,"",iconimage,False,True)

# def addListItem(name='', url='', mode='', iconimage='', isfolder=False, usefullurl=False, customparams={}):
#     if not hasattr(addListItem, "fanart_image"):
#         settings = xbmcaddon.Addon(id="plugin.video.russ-ba")
#         addListItem.fanart_image = settings.getSetting("fanart_image")

#     params = {
#         'url': url,
#         'mode': str(mode),
#         'name': name
#     }
#     params.update(customparams) #merge params with customparams
#     params = urllib.urlencode(params) #urlencode the params

#     generated_url = "%s?%s" % (sys.argv[0], params)
#     liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
#     liz.setInfo( type="Video", infoLabels={ "Title": name } )

#     if addListItem.fanart_image:
#         liz.setProperty('fanart_image', addListItem.fanart_image)

#     if not isfolder:
#         liz.setProperty("IsPlayable", "true")
#     if usefullurl:
#         generated_url = url

#     xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=generated_url, listitem=liz, isFolder=isfolder)
#     return liz
