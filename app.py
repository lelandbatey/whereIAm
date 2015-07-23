#!/bin/sh
"exec" "python" "-B" "$0" "$@"
from __future__ import print_function
from flask import Flask, request
import geo_statistics.angles as angles
import geo_model
import flask
import json

#pylint: disable=W0312
#pylint: disable=C0330

# LOG_FILE_NAME = "gpsRecord.log"

APP = Flask(__name__)

APP.config.update(dict(
	LOG_FILE_PATH="gpsRecord.log",
	DATABASE="location_database.sqlite3"
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

# GPS_DATA = [SEED_DATA]


def get_db():
	"""Returns an instance of the database."""
	database = geo_model.LocationModel(APP.config['DATABASE'])
	database.add_if_empty(SEED_DATA)
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


def make_json_response(in_data):
	"""Returns a proper json response out of the data in passed in."""
	response = flask.make_response(in_data)
	response.headers["Content-type"] = "application/json"
	return response


def jdump(in_data):
	"""Creates prettified json representation of passed in object."""
	return json.dumps(in_data, sort_keys=True, indent=4, separators=(',', ': '))


@APP.route('/')
def main_page():
	"""Renders the main page."""
	return flask.render_template("multi_map.html")


@APP.route('/update', methods=['POST'])
def update():
	"""Logs the request to the log file, as well as adding it to he database."""
	localdb = get_db()

	localdb.new_entry(request.form)
	log_dict(request.form)
	localdb.session.close()
	return ""

@APP.route('/currentpos')
def current_position():
	"""Responds with the latest location in the database."""
	localdb = get_db()

	data = localdb.get_latest()
	data = jdump(data)
	localdb.session.close()
	return make_json_response(data)

@APP.route('/allpos')
def all_positions():
	"""Returns all the location entries in the database, serialized to JSON."""
	localdb = get_db()
	all_data = jdump(localdb.get_all())
	localdb.session.close()
	return make_json_response(all_data)

@APP.route('/entry/id/<int:id_num>')
def get_entry_by_id(id_num):
	"""Returns the entry with the given id."""
	localdb = get_db()
	to_return = localdb.get_id(id_num)
	to_return = jdump(to_return)
	localdb.session.close()
	return make_json_response(to_return)

@APP.route('/entry/id/<int:start_id>/<int:end_id>')
def get_entry_list_by_ids(start_id, end_id):
	"""Returns a list of entries, starting with the `start_id` and ending with the `end_id`."""
	localdb = get_db()
	to_return = localdb.get_id(start_id, end_id)
	to_return = jdump(to_return)
	localdb.session.close()
	return make_json_response(to_return)



@APP.route('/data_range/<float:begin>/<float:end>')
def date_range(begin, end):
	"""Returns all the location entries with timestamps between the given start
	and end. Timestamps are in epoc format."""
	localdb = get_db()
	to_return = localdb.get_date_range(begin, end)
	to_return = angles.calculate_bearing(to_return)
	to_return = jdump(to_return)
	localdb.session.close()
	return make_json_response(to_return)


@APP.route('/last_range')
@APP.route('/last_range/<int:count>')
def last_range(count=50):
	localdb = get_db()
	to_return = localdb.get_last_count(count)
	to_return = angles.calculate_bearing(to_return)
	to_return = jdump(to_return)
	print(to_return)
	localdb.session.close()
	return to_return

if __name__ == '__main__':
	APP.run(host='0.0.0.0', port=8001, debug=True)








