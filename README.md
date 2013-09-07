b3SRLNotify
==========

A bot for notifying users when a SpeedRunsLive race is starting for a game they're interested in.

Message blha303 on irc.speedrunslive.com to set up notifications.

Example message:
----------------

    <b3Notify> Race initiated for Donkey Kong 64. Join #srl-9gcbs to participate.
               http://speedrun.tv/?race=9gcbs

Setup:
------

If you want to run a clone of b3SRLNotify:

* fork this repository
* `virtualenv venv`
* `venv/bin/pip install -r requirements.txt`
* edit config.yml and games.yml
* `venv/bin/python run.py`
