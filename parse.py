#!/usr/bin/env python

from bs4 import BeautifulSoup
from hearthstone import enums

import datetime
import json
import keys
import os
import re
import requests
import sys

if len(sys.argv) != 2:
   print ("Missing filename")
   sys.exit(1)

#file = "/home/amarriner/Dropbox/Hearthstone/logs/S6 Edge/Power_20160219145740.xml"
file = sys.argv[1]

if not os.path.isfile(file):
   print ("No such file " + file)
   sys.exit(1)

URL = "https://trackobot.com/profile/results.json?username=" + keys.username + "&token=" + keys.token

HEROES = {
   "HERO_01": "Warrior",
   "HERO_02": "Shaman",
   "HERO_03": "Rogue",
   "HERO_04": "Paladin",
   "HERO_05": "Hunter",
   "HERO_06": "Druid",
   "HERO_07": "Warlock",
   "HERO_08": "Mage",
   "HERO_09": "Priest"
}

PLAYER = "amarriner"
GAMES = []

f = open(file, "r")
xml = f.read()
f.close()

soup = BeautifulSoup(xml, "xml")

games = soup.find_all("Game")
for game in games:

   start_time = datetime.datetime.strptime(game.attrs["ts"], "%H:%M:%S.%f")
   GAMES.append({
      "player": {},
      "result": {
         "mode": "ranked"
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
   # Determine hero for each player
   #
   for hero in game.find_all("FullEntity", cardID=re.compile("^HERO_[0-9][0-9]$")):
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
   # Find end of game
   #
   for a in game.findAll("Action", entity=1):
       tag = a.find("TagChange", tag=198, value=15)
       if tag:
          # 17:37:38.329882
          end_time = datetime.datetime.strptime(tag.parent.attrs["ts"], "%H:%M:%S.%f")
          GAMES[-1]["result"]["duration"] = (round((end_time - start_time).total_seconds()))

   print (json.dumps({"result": GAMES[-1]["result"]}))
   response = requests.post(URL, data=json.dumps({"result": GAMES[-1]["result"]}), headers={"content-type": "application/json"})
   print (response)
