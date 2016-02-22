# hearthstone-to-trackobot

>Auto Upload Android Hearthstone Power Logs to trackobot.com

This is a hacky project to research uploading [Hearthstone](http://playhearthstone.com) games to [track-o-bot](https://trackobot.com) automatically after theyre played. Obviously track-o-bot does this for you if you're running it on a PC or a Mac, but I was hoping to get it working for Android.

The good news: it works! I was able to get a log to flow through the sequence of steps below and get posted to my track-o-bot profile.

The bad news: it only sorta works, is super kludgey and it takes **way** too many steps. Input is welcome.

## Steps

 + [Enable Logging](#enable-logging)
 + [Sync the Log](#sync-the-log)
 + [Parse the Log](#parse-the-log)

## Enable Logging

In order to do anything with the game data from Hearthstone, first [follow these steps to enable logging](https://github.com/jleclanche/fireplace/wiki/How-to-enable-logging). This will create a Power.log file that will be used for game data in the rest of the process. For this project, I'm enabling it on an Android phone.

## Sync the Log

Since I want to use the stats from an Android install of Hearthstone I need to get the Power.log file off the device and onto something else I can work with more easily (since I'm no Android dev). You might choose something else for this step, but I used [Dropbox](https://dropbox.com) and [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm). I was using [Dropsync](https://play.google.com/store/apps/details?id=com.ttxapps.dropsync), but I think Tasker is a lot better.

I used [this reddit post](https://www.reddit.com/r/tasker/comments/3abjvv/how_to_upload_a_file_to_dropbox_in_the_background/) as an example of how to upload a file to Dropbox. I created that task and then a profile for when Hearthstone exits to fire that task off. This may or may not change depending on how it performs. Sometimes this causes the same log to be uploaded more than once because it's anytime you switch out of the Hearthstone app, not just when it closes. It can always be run manually, too.

Would love to find a better way to do this as this seems like the worst part. The other steps can use improvement, too, but this one feels like the hardest to streamline.

## Parse the Log

Once the log is uploaded to Dropbox, I can process it. I have the [Dropbox linux client](https://www.dropbox.com/install?os=lnx) installed and am syncing only the Hearthstone/logs/* directories. You can obviously sync whatever you want, but I didn't want everything synced to this machine.

I created [a shell script](power_cycle.sh) that enables [inotify](https://en.wikipedia.org/wiki/Inotify) for the logs/* directories to watch for uploads of Power.log and process them:

 + Renames the Power.log file to Power_%Y%m%d%H%M%S.log so that it's not accidentally overwritten
 + Runs the [Hearthsim python implementation of HSReplay](https://github.com/hearthsim/hsreplay) to convert the log to the [HSReplay XML Spec](http://hearthsim.info/hsreplay/). Not strictly necessary, but wanted to use the more formalized spec.
 + Runs [parse.sh](parse.sh) which executes [parse.py](parse.py). This runs through the replay to generate a JSON string for each game in the [track-o-bot API format](https://gist.github.com/stevschmid/120adcbc5f1f7cb31bc5) and then uploads them one at a time.
 + Should probably delete the logs at some point, but doesn't currently.
  
#### track-o-bot API
 
To use [track-o-bot API](https://gist.github.com/stevschmid/120adcbc5f1f7cb31bc5), you need a username and an API key. Install the track-o-bot software on a PC or Mac, open your profile from that app and go to your [Settings->API](https://trackobot.com/profile/settings/api) page to get that data. I put it in a keys.py file in the same directory as the [parse.py](parse.py) file so that script can use them upon uploading.

#### Some Problems With This
 + There isn't a way to get whether a game is ranked, casual, tavern brawl, or arena from the Power.log so I'm defaulting to ranked because that's what I play most often.
 + I'm not currently parsing card plays to leverage track-o-bots auto deck identification, but this can definitely be done
 
---
 
