import requests
from utils import *
from game import Game
from common import *

import urlparse

class NeuLion():
  def __init__(self):
    self.session = getSession()

  def getGame(self, year, weekStart, id):
    games = self.getGamesForWeek(year, weekStart)

    for g in games:
      if g.id == id:
        return g

  def getGames(self, dt):
    return self.getGamesForWeek(dt.year, '%d_%d' % (dt.month, dt.day))

  def getGamesForWeek(self, year, weekStart):
    url = 'http://smb.cdnak.neulion.com/fs/nba/feeds_s2012/schedule/%s/%s.js' % (year, weekStart)
    params = {'t': myNow().time()}

    try:
      r = self.session.get(url, params=params)
      r.raise_for_status()
      content = r.text
      games = json.loads(content[content.find("{"):], object_hook=Game.jsonToGame)
      weekStart = weekStart
      for g in games:
        g.weekStart = weekStart
        g.year = year
      return games
    except requests.exceptions.HTTPError as e:
      print 'NBA League Pass - Error logging in: %s' % str(e)

neulion = NeuLion()