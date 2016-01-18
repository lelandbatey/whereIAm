# Where I Am

Shows where you are on a map for all the world to see.

[***DEMO***](http://whereis.lelandbatey.com/)

## Requirements

WIA is written in Python using [Flask.](http://flask.pocoo.org/) Additionally, the GPS data is reported every few minutes by the [Big Brother GPS App](https://play.google.com/store/apps/details?id=org.gnarf.bigbrother.gps&hl=en) for Android.

To install the appropriate requirements:

    pip install -r requirements.txt

Install BigBrother GPS on the Android device of your choice through the play store. I currently have it report it's location to the server every two minutes. I'd also recommend using an extended battery if possible, as frequents GPS activity can impact battery life.

## Installation

To install, clone the repo into whatever folder you'd like. From there, you can run it nakedly on port 80 (not usually recommended), or you can run it on different port and use a reverse proxy (Apache, Nginx, etc) to handle the traffic however you like (recommended).

## NOTES

All location responses are written to SQLite database in this directory as well as appended to a log file in this directory.

### Log File Format

The log file is in a non-standard format, similar in spirit to CSV. Here is an
example line from that log file:

    bearing=0.0,provider=network,latitude=46.3228938,altitude=0.0,time=2014-02-20T04:55:49.603Z,speed=0.0,longitude=-119.2677629,accuracy=38.618

This is meant to represent the following JSON dictionary:

	{
	   "accuracy": "38.618",
	   "altitude": "0.0",
	   "bearing": "0.0",
	   "latitude": "46.3228938",
	   "longitude": "-119.2677629",
	   "provider": "network",
	   "speed": "0.0",
	   "time": "2014-02-20T04:55:49.603Z"
	}

A brief description of the format:

> Stores a non-nested dictionary object on a single line. Each key-value pair
> is represented as `key=value`, and each key-value pair is separated by a
> comma. This does not handle nested dictionaries, nor does it handle
> keys/values in any format other than `str`, `int`, or `float` formats.

It is used in this case because of the very simple structure of the data.
Should the functionality of this program be extended such that this format no
longer meets the storage needs of the project, it will be scraped in favor of
a longer term solution such as Sqlite.

