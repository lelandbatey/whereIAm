#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Frontend for whereIAm, exposing http api for getting locations"""

from __future__ import print_function
from os.path import dirname, realpath, join

import flask
import requests

from ..models import geo_utils, entry_model

#pylint: disable=W0312
#pylint: disable=C0330


APP = flask.Flask(__name__,
	template_folder=join(dirname(realpath(__file__)), "templates"),
	static_folder=join(dirname(realpath(__file__)), "static"))


APP.config.update(dict(
	LOG_FILE_PATH="gpsRecord.log",
	DATABASE=join(dirname(realpath(__file__)), "../../location_database.sqlite3")
))


# Seed data will always be the first entry in whatever database is started
SEED_DATA = {
	"accuracy"  : "38.618",
	"altitude"  : "0.0",
	"bearing"   : "0.0",
	"latitude"  : "46.3228938",
	"longitude" : "-119.2677629",
	"provider"  : "network",
	"speed"     : "0.0",
	"time"      : "2014-02-20T04:55:49.603Z"
}


def get_db():
	"""Returns an instance of the database."""
	database = entry_model.LocationModel(APP.config['DATABASE'])
	return database


def dict_to_oneline(in_dict):
	"""Serializes a dictionary to a string that fits on one line."""
	ret_val = ""
	temp = [str(x)+"="+str(in_dict[x]) for x in in_dict.keys()]
	# The above list comprehension is the equivelent of the following
	# for x in in_dict.keys():
	# 	temp.append(str(x)+"="+str(in_dict[x]))

	ret_val = ','.join(temp)
	return ret_val+'\n'


def log_dict(in_dict):
	"""Logs a dictionary to the log file specified via 'LOG_FILE_PATH'. Logs the
	dictionary in special single line format."""
	record_file = open(APP.config['LOG_FILE_PATH'], 'a')
	record_file.write(dict_to_oneline(in_dict))
	record_file.close()
	return

def jdump(in_data):
	"""Creates prettified json representation of passed in object."""
	return flask.json.dumps(in_data, sort_keys=True, indent=4, separators=(',', ': '))

def make_json_response(in_data):
	"""Returns a proper json response out of the data passed in."""
	if not isinstance(in_data, str):
		in_data = jdump(in_data)
	response = flask.make_response(in_data)
	response.headers["Content-type"] = "application/json"
	return response



class AutoDB(object):
	"""Eases database calls by handling creation and cleanup of database"""
	def __getattr__(self, name):
		def db_func(*args, **kwargs):
			database = get_db()
			db_method = getattr(database, name)
			return_value = db_method(*args, **kwargs)
			database.session.close()
			return return_value
		return db_func

class AutoQuery(object):
	"""Does everything for you."""
	def __init__(self, before_hook=None):
		self.before_hook = before_hook
	def __getattr__(self, name):
		def query_func(*args, **kwargs):
			dbf = getattr(AutoDB(), name)
			return_value = dbf(*args, **kwargs)
			if self.before_hook:
				return_value = self.before_hook(return_value)
			return make_json_response(return_value)
		return query_func


@APP.route('/')
def main_page():
	"""Renders the main page."""
	return flask.render_template("mainpage.html")


@APP.route('/api/v1/entry', methods=['POST'])
@APP.route('/api/v1/update', methods=['POST'])
def update():
	"""Logs the request to the log file, as well as adding it to he database."""
	AutoDB().new_entry(flask.request.form)
	log_dict(flask.request.form)
	return "Success"

@APP.route('/api/v1/entry', methods=['GET'])
@APP.route('/api/v1/currentpos')
def current_position():
	"""Responds with the latest location in the database."""
	latest = AutoDB().get_latest()
	if latest:
		return make_json_response(latest)
	else:
		return make_json_response(SEED_DATA)

@APP.route('/api/v1/allpos')
def all_positions():
	"""Returns all the location entries in the database, serialized to JSON."""
	return AutoQuery().get_all()

@APP.route('/api/v1/entry/id/<int:id_num>')
def get_entry_by_id(id_num):
	"""Returns the entry with the given id."""
	return AutoQuery().get_id(id_num)

@APP.route('/api/v1/entry/id/<int:start_id>/<int:end_id>')
def get_entry_list_by_ids(start_id, end_id):
	"""Return list of entries, starting with `start_id` and ending with `end_id`."""
	return AutoQuery().get_id_range(start_id, end_id)

@APP.route('/api/v1/entry/time/<entry_time>')
def get_entry_by_time(entry_time):
	"""Returns the entry with the time nearest the given time"""
	entry_time = float(entry_time)
	return AutoQuery().get_time(entry_time)

@APP.route('/api/v1/entry/time/<begin>/<end>')
@APP.route('/api/v1/data_range/<begin>/<end>')
def date_range(begin, end):
	"""Returns all the location entries with timestamps between the given start
	and end. Timestamps are in epoc format."""
	begin, end = float(begin), float(end)
	return AutoQuery().get_date_range(begin, end)


@APP.route('/api/v1/last_range')
@APP.route('/api/v1/last_range/<int:count>')
def last_range(count=50):
	return AutoQuery().get_last_count(count)

@APP.route('/api/v1/time_to_place/<path:location>')
def time_to_place(location):
	if not location:
		return ""
	latest = AutoDB().get_latest()
	lat, lng = latest['latitude'], latest['longitude']

	# Construct the query parameter
	apikey = 'AIzaSyD3CgE-0aPdTDT_Ts4pud_9_1ZCykAF5IE'

	query_path = 'https://maps.googleapis.com/maps/api/distancematrix/json'
	params_template = '?origins={},{}&destinations={}&mode=driving&key={}'

	query_url = "{}{}".format(query_path, params_template.format(lat, lng, location, apikey))

	# Get the distance matrix data from Google
	req = requests.get(query_url)
	data = req.json()
	return make_json_response(data)



if __name__ == '__main__':
	APP.run(host='0.0.0.0', port=8001, debug=True)

