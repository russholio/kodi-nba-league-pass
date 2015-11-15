from utils import *
from team import Team

class Game():
  def __init__(self, id=None, homeTeam=None, visitors=None, homeScore=0, visitorScore=0, periods=None, scheduledTime=None, startTime=None, endTime=None, status=0, feeds={}, comment='', season=None):
    self.id = id
    self.homeTeam = Team(homeTeam)
    self.visitors = Team(visitors)
    self.homeScore = homeScore
    self.visitorScore = visitorScore
    self.periods = periods
    self.startTime = None
    self.endTime = None
    self.status = status
    self.scheduledTime = None
    self.comment = comment
    self.season = season
    self.weekStart = None
    self.feeds = feeds
    if startTime:
      self.startTime = gameTime(startTime)
    if endTime:
      self.endTime = gameTime(endTime)
    if scheduledTime:
      self.scheduledTime = gmtTime(scheduledTime)

  @property
  def day(self):
    return self.startTime.day if self.startTime else self.scheduledTime.day

  @property
  def month(self):
    return self.startTime.month if self.startTime else self.scheduledTime.month

  @property
  def year(self):
    return self.startTime.year if self.startTime else self.scheduledTime.year

  def __repr__(self):
    return '%s vs. %s on %s' % (self.homeTeam, self.visitors, str(self.startTime))

  # Return a list of games
  @staticmethod
  def filterGamesForTeam(team, a):
    """Filter the supplied list and return a new list of games containing only games for that team"""
    newa = []
    for g in a:
      if g.homeTeam == team or g.visitors == team:
        newa.append(g)
    return newa

  # Return a list of live games and removes from the original
  @staticmethod
  def extractLiveGames(now, a):
    grace = timedelta(minutes=15)
    start = now + grace
    end = now - grace
    liveGames = []
    i = 0
    while i < len(a):
      g = a[i]
      if g.status == 1:
        liveGames.append(a.pop(i))
      else:
        i += 1
    return liveGames

  # Return a list of live games and removes from the original
  @staticmethod
  def extractTopPicks(now, a):
    topGames = []
    i = 0
    while i < len(a):
      g = a[i]
      if (g.periods > 4) or (abs(g.homeScore - g.visitorScore) < 10):
        topGames.append(a.pop(i))
      else:
        i += 1
    return topGames

  # Return a list of live games and removes from the original
  @staticmethod
  def extractPastGames(now, a):
    pastGames = []
    i = 0
    while i < len(a):
      g = a[i]
      if g.endTime and g.endTime < now:
        pastGames.append(a.pop(i))
      else:
        i += 1
    pastGames.reverse()
    return pastGames

  @staticmethod
  def jsonToGame(js):
    if 'games' in js:
      games = []
      for k in js['games']:
        if len(k):
          for g in k:
            games.append(Game(id=g['id'], homeTeam=g['h'], visitors=g['v'], homeScore=g.get('hs'), visitorScore=g.get('vs'), periods=g.get('p'), startTime=g.get('st'), endTime=g.get('et'), scheduledTime=g.get('d'), status=g.get('gs'), feeds=g.get('video'), comment=g.get('c'), season=g.get('s')))
      return games
    return js

  @staticmethod
  def jsonToFeeds(js):
    feeds = {
      'home': Feed(js.get('f').get('id')) if js.get('f') else False,
      'away': Feed(js.get('af').get('id')) if js.get('af') else False,
      'condensed': Feed(js.get('c').get('id')) if js.get('c') else False
    }
    return feeds

class Feed():
  def __init__(self, id=None):
    self.id = id
