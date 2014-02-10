UntitledMixtapes
================

UntitledMixtapes is a Spotify mixtape-style playlist generator.

Given a track and initial settings, the app queries last.fm and EchoNest APIs to find and order songs based on artist similarity and song properties like "energy" and tempo. The result is displayed embedded in the browser using Spotify's web widgets.

UntitledMixtapes is written mostly in Python and uses Flask to communicate with the back-end. The web interface was designed based off of Bootstrap, with additional JQuery functionality added.


Background
==========

UntitledMixtapes was originally created during [HackBeanpot 2014](http://www.hackbeanpot.com/), a 40-hour hackathon. The app won the award for Best Use of APIs, sponsored by SmarterTravel. It was created and is actively maintained by [Nat Dempkowski](https://github.com/natdempk), [Zack Hickman](https://github.com/zdhickman), and [Sanders Lauture](https://github.com/golf1052).
