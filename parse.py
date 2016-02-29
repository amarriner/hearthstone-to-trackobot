#!/usr/bin/env python

from bs4 import BeautifulSoup
from hearthstone import enums

import datetime
import json
import keys
import math
import os
import pytz
import re
import requests
import sys

CWD = os.path.dirname(__file__)

# 
# Load cached cards.json from https://api.hearthstonejson.com/v1/latest/enUS/cards.json
#
f = open(CWD + "/cards.json", "r")
CARDS = json.loads(f.read())
f.close

#
# Find a card by its ID
#
def get_card(id):
   for c in filter(lambda card: card['id'] == id, CARDS):
      return c

if len(sys.argv) != 2:
   print ("Missing filename")
   sys.exit(1)

file = sys.argv[1]

if not os.path.isfile(file):
   print ("No such file " + file)
   sys.exit(1)

print("Processing file " + file + " ...")

#
# Open HSReplay formatted file
#
f = open(file, "r")
xml = f.read()
f.close()

#
# Get creation date of file for use in upload to API. Not perfect because the date
# of the file may not always be the date of the game, but since the date is not 
# in the log, this is a decent approximation. This also relies on the timezone set
# below to be the same as the timezone the game was played in. Since the game may
# or may not have been set on the same machine as the process is running that
# might cause problems as well. Best to have all of them set to the same TZ.
#
TZ = pytz.timezone('US/Eastern')
CTIME = datetime.date.fromtimestamp(os.path.getctime(file))

URL = "https://trackobot.com/profile/results.json?username=" + keys.username + "&token=" + keys.token
HISTORY = "https://trackobot.com/profile.csv?token=" + keys.token + "&username=" + keys.username

ENTITIES = {}

HEROES = {
   "HERO_01": "Warrior",
   "HERO_01a": "Warrior",
   "HERO_02": "Shaman",
   "HERO_03": "Rogue",
   "HERO_04": "Paladin",
   "HERO_05": "Hunter",
   "HERO_05a": "Hunter",
   "HERO_06": "Druid",
   "HERO_07": "Warlock",
   "HERO_08": "Mage",
   "HERO_08a": "Mage",
   "HERO_09": "Priest"
}

TURN = 1
PLAYER = "amarriner"
GAMES = []

#
# Get the mode to send via the API (ranked, casual, etc)
#
f = open(CWD + "/mode", "r")
mode = f.read().replace("\n","")
f.close()

#
# Get the rank
#
f = open(CWD + "/rank", "r")
rank = f.read().replace("\n","")
f.close()

soup = BeautifulSoup(xml, "xml")

games = soup.find_all("Game")
for game in games:

   print("Processing game with timestamp " + game.attrs["ts"] + " ...")

   start_time = datetime.datetime.strptime(game.attrs["ts"], "%H:%M:%S.%f")
   added = TZ.localize(datetime.datetime.strptime(CTIME.strftime("%Y-%m-%d") + " " + start_time.strftime("%H:%M:%S"), "%Y-%m-%d %H:%M:%S"))

   HERO_POWERS = {}
   SECRETS = {}

   #
   # Check to see if we've already done this timestamp
   #
   f = open(CWD + "/games", "r")
   timestamps = f.read().split("\n")
   f.close()

   if game.attrs["ts"] in timestamps:
      print ("Already processed this timestamp")
      continue

   #
   # If not, save it so we don't repeat it
   #
   f = open(CWD + "/games", "a")
   f.write(game.attrs["ts"] + "\n")
   f.close()

   GAMES.append({
      "player": {},
      "result": {
         "added": added.isoformat(),
         "mode": mode,
         "card_history": []
      }
   })

   #
   # Set player in game
   #   
   for player in game.find_all("Player"):
      if player.attrs["name"] == PLAYER:
         GAMES[-1]["player"] = {
            "id": player.attrs["id"],
            "name": player.attrs["name"],
            "playerID": player.attrs["playerID"]
      }

   #
   # Find entities, which are eventually cards played
   #
   for e in game.find_all("FullEntity"):
      cID = ''
      if 'cardID' in e.attrs.keys():
         cID = e.attrs['cardID']

         card = get_card(cID);
         if card['type'] == "HERO_POWER":
            HERO_POWERS[e.attrs['id']] = card

      mana = 0
      t = e.find('Tag', tag=48)
      if t:
         mana = int(t.attrs['value'])

      who = 'opponent'
      if e.find('Tag', tag=50).attrs['value'] == GAMES[-1]['player']['playerID']:
         who = 'me'

      ENTITIES[e.attrs['id']] = { 'player': who, 'card_id': cID, 'mana': mana }

   #
   # Populate entities that are filled out after game start 
   #
   for e in game.find_all("ShowEntity", cardID=re.compile(".*")):

      mana = 0
      t = e.find('Tag', tag=48)
      if t:
         mana = int(t.attrs['value'])

      ENTITIES[e.attrs['entity']]['card_id'] = e.attrs['cardID']
      ENTITIES[e.attrs['entity']]['mana'] = mana

   #
   # Find secrets: TagChange tag with a zone (49) of secret (7)
   #
   for t in game.find_all("TagChange", tag="49", value="7"):
      if ENTITIES[t.attrs['entity']]['card_id']:
         SECRETS[t.attrs['entity']] = get_card(ENTITIES[t.attrs['entity']]['card_id'])

   #
   # Determine hero for each player
   #
   for hero in game.find_all("FullEntity", cardID=re.compile("^HERO_[0-9][0-9][a-zA-Z0-9]?$")):
      controller = hero.find("Tag", tag=50).attrs["value"]
      hero_str = hero.attrs["cardID"]

      if controller == GAMES[-1]["player"]["playerID"]:
         GAMES[-1]["result"]["hero"] = HEROES[hero.attrs["cardID"]]
      else:
         GAMES[-1]["result"]["opponent"] = HEROES[hero.attrs["cardID"]]

   #
   # Find coin and assign to player
   #
   coin_entity = game.find("FullEntity", cardID="GAME_005")
   if coin_entity:
      coin_controller = coin_entity.find("Tag", tag=50).attrs["value"]

      if coin_controller == GAMES[-1]["player"]["playerID"]:
         GAMES[-1]["result"]["coin"] = True
   
   else:
      GAMES[-1]["result"]["coin"] = False

   #
   # Determine winner
   #
   winner = game.find("TagChange", tag=17, value=4)
   if GAMES[-1]["player"]["id"] == winner.attrs["entity"]:
      GAMES[-1]["result"]["win"] = True
   else:
      GAMES[-1]["result"]["win"] = False

   #
   # Loop through all actions
   #
   for a in game.findAll("Action"):
       
       #
       # If this is the game entity
       #
       if int(a.attrs['entity']) == 1:

          #
          # Find end of game
          #
          tag = a.find("TagChange", tag=198, value=15)
          if tag:
             # 17:37:38.329882
             end_time = datetime.datetime.strptime(tag.parent.attrs["ts"], "%H:%M:%S.%f")
             GAMES[-1]["result"]["duration"] = (round((end_time - start_time).total_seconds()))

          #
          # Look for turn change
          #
          if a.find("TagChange", tag=20):
             TURN = a.find("TagChange", tag=20).attrs['value']

       #
       # If this is not the game or either of the players
       #
       if int(a.attrs['entity']) > 3:

          if int(TURN) > 1:

             #
             # Find played cards
             #
             t = a.find("TagChange", tag=261)
             if t and t.attrs['entity'] not in HERO_POWERS.keys():
                card = get_card(ENTITIES[a.attrs['entity']]['card_id'])
                if card['type'] in ['WEAPON', 'MINION', 'SPELL']:
                   ENTITIES[a.attrs['entity']]['turn'] = math.ceil(int(TURN) / 2)
                   GAMES[-1]["result"]["card_history"].append(dict(ENTITIES[a.attrs['entity']]))

             #
             # Or if this is a hero power. Check to make sure Action is top level (right below Game). I think
             # the type can be used, too, (PowSubType enum?)
             #
             if a.attrs['entity'] in HERO_POWERS.keys() and a.parent.name == 'Game':
                ENTITIES[a.attrs['entity']]['turn'] = math.ceil(int(TURN) / 2)
                GAMES[-1]["result"]["card_history"].append(dict(ENTITIES[a.attrs['entity']]))

             #
             # Or if a secret was revealed
             #
             if a.attrs['entity'] in SECRETS.keys():
                ENTITIES[a.attrs['entity']]['turn'] = math.ceil(int(TURN) / 2)
                GAMES[-1]["result"]["card_history"].append(dict(ENTITIES[a.attrs['entity']]))

   if mode == "ranked" and rank:
      GAMES[-1]["result"]["rank"] = rank

   print ("Uploading game...")
   response = requests.post(URL, data=json.dumps({"result": GAMES[-1]["result"]}), headers={"content-type": "application/json"})
   print (response.status_code)

#
# Get full history as backup
#
print ("Getting full history...")
response = requests.get(HISTORY)

f = open("history.csv", "w")
f.write (response.text)
f.close()
