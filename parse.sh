#!/bin/sh

. /home/amarriner/.virtualenvs/hearthstone-parse/bin/activate
/home/amarriner/python/hearthstone-parse/parse.py "$1"
deactivate
