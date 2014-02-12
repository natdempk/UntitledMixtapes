UntitledMixtapes
================

UntitledMixtapes is a Spotify mixtape-style playlist generator.

Given a track and initial settings, the app queries last.fm and EchoNest APIs to find and order songs based on artist similarity and song properties like "energy" and tempo. The result is displayed embedded in the browser using Spotify's web widgets.

UntitledMixtapes is written mostly in Python and uses Flask to communicate with the back-end. The web interface was designed based off of Bootstrap, with additional JQuery functionality added.


Background
==========

UntitledMixtapes was originally created during [HackBeanpot 2014](http://www.hackbeanpot.com/), a 40-hour hackathon. The app won the award for Best Use of APIs, sponsored by SmarterTravel. It was created and is actively maintained by [Nat Dempkowski](https://github.com/natdempk), [Zack Hickman](https://github.com/zdhickman), and [Sanders Lauture](https://github.com/golf1052).

Usage
=====
If you want to run/host this yourself, first you'll want to install the Python requirements with `pip install -r requirements.txt`. We use python 2.7.6, but any 2.7.X should work. Next you'll need an API key from EchoNest, a last.fm account, and a last.fm API key. Put those values as strings into `config_example.py` and rename the file to config.py. Untitled Mixtapes can then be run with `python playlist.py`. A Procfile is even included which means the project is ready to be pushed to Heroku with a couple commands. On Heroku, gunicorn is required as specified by the Procfile. You can test gunicorn is working locally if you have the Heroku Toolbelt installed by running `foreman start`. To deploy to Heroku you can simply run `heroku create` and `git push heroku master`.
