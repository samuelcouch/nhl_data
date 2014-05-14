
# coding: utf-8

# In[4]:

import requests
import tablib
import re
from bs4 import BeautifulSoup
from urlparse import urlparse
import html5lib


# In[5]:

data = tablib.Dataset()

data.headers = ['game date', 'away', 'home', 'espn id', 'home score', 'away score']

root_url = 'http://scores.espn.go.com/nhl/scoreboard?date='

month_schedule = {'oct': {'start': 20131001, 'end': 20131031},
                  'nov': {'start': 20131101, 'end': 20131130},
                  'dec': {'start': 20131201, 'end': 20131231},
                  'jan': {'start': 20140101, 'end': 20140131},
                  'feb': {'start': 20140201, 'end': 20140228},
                  'mar': {'start': 20140301, 'end': 20140331},
                  'apr': {'start': 20140401, 'end': 20140430},
                  'may': {'start': 20140501, 'end': 20140531}}
flagged = tablib.Dataset()
flagged.headers = ['espn id']


# In[ ]:

def games_for_day(soup):
    return soup.find_all(id=re.compile('gamebox'))


# In[ ]:

def extract_date(soup):
    html = soup.find(class_=re.compile('key-dates'))
    text = html.find('h2').text
    date = text.split()[2:]
    return ' '.join(date)


# In[ ]:

def away(soup):
    s = soup.find(id=re.compile('awayHeader')).find(class_='team-name').text
    clean_text = s.split()
    away_team = ' '.join(clean_text)
    return away_team


# In[ ]:

def home(soup):
    s = soup.find(id=re.compile('homeHeader')).find(class_='team-name').text
    clean_text= s.split()
    home_team = ' '.join(clean_text)
    return home_team


# In[6]:

def getScores(gameID):
    scores = {}
    url = 'http://espn.go.com/nhl/playbyplay?gameId='+str(gameID)+'&period=0'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    try:
        scores['away'] = soup.find(class_='gp-awayScore').text
    except AttributeError:
        scores['away'] = ""
        flagged.append([gameID])
    try:
        scores['home'] = soup.find(class_='gp-homeScore').text
    except AttributeError:
        scores['home'] = ""
        flagged.append([gameID])
    return scores


# In[ ]:

def espn_id_link(soup):
    links = soup.find(id=re.compile('gameLinks')).find_all('a')
    for link in links:
        if 'conversation' in link['href']:
            text = link['href']
    return text


# In[ ]:

def espn_id(soup):
    text = espn_id_link(soup).split('=')
    espn_id = text[-1]
    return espn_id


# In[ ]:

team_names = {'Devils': 'NJD', 'Blackhawks': 'CHI', 'Islanders': 'NYI', 
              'Blue Jackets': 'CBJ', 'Rangers': 'NYR', 'Red Wings': 'DET', 
              'Flyers': 'PHI', 'Predators':'NSH', 'Penguins': 'PIT',
              'Blues': 'STL', 'Bruins': 'BOS',  'Sabres': 'BUF',
              'Avalanche': 'COL', 'Canadiens': 'MTL', 'Oilers': 'EDM', 
              'Senators': 'OTT', 'Wild': 'MIN', 'Maple Leafs': 'TOR', 
              'Canucks': 'VAN', 'Hurricanes': 'CAR', 'Ducks': 'ANA', 
              'Panthers': 'FLA', 'Stars': 'DAL', 'Lightning': 'TBL', 
              'Kings': 'LAK', 'Capitals': 'WSH', 'Coyotes': 'PHX', 
              'Jets': 'WPG', 'Sharks': 'SJS', 'Flames': 'CGY'}


# In[2]:

def make_schedule():
    # Will make nhl schedule for games to be played
    for month in month_schedule:
        for day in range(month_schedule.get(month).get('start'), month_schedule.get(month).get('end')):
            url = root_url + str(day)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html5lib')
            for x in games_for_day(soup):
                away = team_names.get(away(x))
                home = team_names.get(home(x))
                espnID = espn_id(x)
                scores = getScores(espnID)
                data.append([str(day), away, home, espnID, scores['home'], scores['away']])


# In[ ]:

make_schedule()


# In[7]:

open('20132014_games.xls', 'w').write(data.xls)
open('flagged_games.xls', 'w').write(flagged.xls)


# In[8]:

with open('20132014_games.csv', 'wb') as f:
    f.write(data.csv)
with open('flagged_games.csv', 'wb') as f:
    f.write(flagged.csv)


# In[ ]:



