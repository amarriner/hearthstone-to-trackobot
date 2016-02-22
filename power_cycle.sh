#!/bin/sh

HOME="/home/amarriner"
BASE_DIR="${HOME}/Dropbox/Hearthstone/logs"
PYTHON=${HOME}/.localpython-3.4.2/bin/python3.4
HSREPLAY=${HOME}/python/HSReplay/python/convert.py
HSPARSE=${HOME}/python/hearthstone-parse/parse.sh
LOGDIR=${HOME}/logs/hearthstone-parse

cd $BASE_DIR

inotifywait -q --format "%w%f" -mr -e close . |
   while read -r file; do
      DIR=`echo "$file" | cut -f2 -d"/"`
      FILE=`echo "$file" | cut -f3 -d"/"`
      if [ "$FILE" = "Power.log" ]; then
         if [ -f "$file" ]; then
            TS=`date +%Y%m%d%H%M%S`
            mv "$file" "$DIR/Power_${TS}.log"

            $PYTHON $HSREPLAY "$DIR/Power_${TS}.log" > "$DIR/Power_${TS}.xml" 
            $HSPARSE "$DIR/Power_${TS}.xml" > ${LOGDIR}/hearthstone-parse.log
         fi
      fi
   done
