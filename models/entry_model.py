from __future__ import print_function
from sqlalchemy import create_engine
import datetime
import json


#pylint: disable=W0312

def json_dump(indata):
	"""Creates prettified json representation of passed in object."""
	return json.dumps(indata, sort_keys=True, indent=4, \
		separators=(',', ': '))#, cls=date_handler)
def jp(indata):
	"""Prints json representation of object"""
	print(json_dump(indata))


def epoch_to_datetime(epoch):
	"""Converts an epoch timestamp to datetime."""
	return datetime.datetime.fromtimestamp(epoch)

def datetime_to_epoch(indate):
	"""Converts a datetime object to an epoch timestamp."""
	return (indate - datetime.datetime(1970, 1, 1)).total_seconds()

def validate_entry_data(in_data):
	"""Validates that an entry has the correct keys/attributes."""
	attrs = ['longitude', 'latitude', 'time']
	for attr in attrs:
		if attr not in in_data:
			raise KeyError("Data invalid; requires a '{}' attribute".format(attr))


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker


BASE = declarative_base()

class LocationEntry(BASE):
	"""Model for an entry into the log of geographic data."""
	__tablename__ = "location_entries"
	id_num = Column(Integer, primary_key=True)
	longitude = Column(Float)
	latitude = Column(Float)
	timestamp = Column(String)
	# monotonic_timestamp exists so we can do range queries, such as getting
	# all objects between a start and end time.
	monotonic_timestamp = Column(Integer)
	# A response from the device will always include longitude, latitude, and
	# timestamp, but it will also usually include other parameters. However,
	# those parameters are not garuanteed to be sent. For that reason, we will
	# store the raw request from the client in JSON form here
	raw_request = Column(String)
	data = {}

	def __init__(self, raw_request):
		"""Translates dict of values into DB object."""
		self.raw_request = json_dump(raw_request)
		self.longitude = float(raw_request['longitude'])
		self.latitude = float(raw_request['latitude'])
		# Handles different names for the same thing
		for key in ['timestamp', 'time']:
			if key in raw_request:
				self.timestamp = raw_request[key]
				break
		self.parsed_timestamp = datetime.datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
		self.monotonic_timestamp = datetime_to_epoch(self.parsed_timestamp)
		self.data = {}

	@property
	def json(self):
		"""Returns json object representation of object."""
		to_return = json.loads(self.raw_request)
		for key in self.data:
			to_return[key] = self.data[key]
		to_return['monotonic_timestamp'] = self.monotonic_timestamp
		to_return['id'] = self.id_num
		return to_return


class LocationModel(object):
	"""Model for database holding location data, with SQLAlchemy backend."""
	def __init__(self, db_name="location_database.sqlite3"):
		self.db_name = db_name
		self.db = create_engine('sqlite:///'+db_name)
		self.session_class = sessionmaker()
		self.session_class.configure(bind=self.db)
		self.session = self.session_class()
		# Creates database with tables, unless they already exist.
		LocationEntry.metadata.create_all(self.db, checkfirst=True)

	def add_if_empty(self, request):
		"""Adds a request if the table is otherwise empty."""
		entry = self.session.query(LocationEntry)\
		            .order_by(LocationEntry.id_num).first()
		if not entry:
			self.new_entry(request)

	def new_entry(self, request, commit=True):
		"""Stores a request into the database."""
		entry = LocationEntry(request)
		self.session.add(entry)
		if commit:
			self.session.commit()

	def get_date_range(self, begin_date, end_date):
		"""Gets all entries that exist between the begin and end dates.
		Accepts either datetime objects or numbers representing a date."""
		if isinstance(begin_date, datetime.datetime):
			begin_date = datetime_to_epoch(begin_date)
			end_date = datetime_to_epoch(end_date)
		entries = self.session.query(LocationEntry).filter(
			LocationEntry.monotonic_timestamp >= begin_date,
			LocationEntry.monotonic_timestamp <= end_date
		)
		to_return = [x for x in entries]
		to_return = speed_for_series(to_return)
		to_return = [x.json for x in to_return]
		# Removes data from when not moving.
		# to_return = [x for x in to_return if float(x['bearing']) != 0]
		# jp(to_return)
		return to_return

	def get_latest(self):
		"""Returns the latest LocationEntry which has been added to the db."""
		entry = self.session.query(LocationEntry)\
		            .order_by(LocationEntry.id_num.desc())\
		            .first()
		return entry.json

	def get_last_count(self, count=50):
		"""Gets the latest `count` number of LocationEntrys."""
		entries = self.session.query(LocationEntry)\
		              .order_by(LocationEntry.id_num)\
		              .limit(count)
		return [x.json for x in entries]

	def get_all(self):
		"""Returns all the LocationEntry objects in order they where stored"""
		entries = self.session.query(LocationEntry)\
		              .order_by(LocationEntry.id_num)
		to_return = [x.json for x in entries]
		return to_return

	def get_id(self, id_to_query):
		"""Returns the LocationEntry object with the given id."""
		entry = self.session.query(LocationEntry).filter(
			LocationEntry.id_num == id_to_query
		).first()
		return entry.json

	def get_id_range(self, start_id, end_id):
		"""Returns all LocationEntry objects with ids on or between start_id and end_id"""
		entries = self.session.query(LocationEntry).filter(
			LocationEntry.id_num >= start_id,
			LocationEntry.id_num <= end_id
		)
		to_return = [x for x in entries]
		to_return = speed_for_series(to_return)
		to_return = [x.json for x in to_return]
		return to_return


import math
# Below taken from here:
#     http://www.johndcook.com/blog/python_longitude_latitude/
def distance_on_unit_sphere(lat1, long1, lat2, long2):
	"""Calculates the distance between two lat/long points. Returns distance in
	'arc length' format that's relative to the radius of earth. To get the
	distance in miles, multiply the result by 3960, while to get the distance
	in kilometers multiply the result by 6373."""
	# Convert latitude and longitude to
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0

	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians

	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians

	# Compute spherical distance from spherical coordinates.

	# For two locations in spherical coordinates
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) =
	#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length

	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
	cos = min(1, max(cos, -1))
	try:
		arc = math.acos(cos)
	except Exception, e:
		#print("Cos:", cos)
		#print(e)
		raise e

	# Remember to multiply arc by the radius of the earth
	# in your favorite set of units to get length.
	return arc


def get_speed(entry0, entry1):
	"""Given two 'LocationEntry' objects, returns speed traveled between the
	two them. Return value is in form of meters per second."""

	arc_distance = distance_on_unit_sphere(entry0.latitude, entry0.longitude, entry1.latitude, entry1.longitude)
	# Multiplying the arc distance by the radius of the earth in meters. Gets
	# us the distance in meters.
	distance = arc_distance * 6378100
	time = entry1.monotonic_timestamp - entry0.monotonic_timestamp
	return distance / time

def speed_for_series(entries):
	"""Function prints information on a series of 'LocationEntry' objects."""
	for i in range(0, len(entries)-2):
		speed_meters_ps = get_speed(entries[i], entries[i+1])
		# print("Speed in m/s:", speed_meters_ps)
		kilometers_ph = (speed_meters_ps * 3600.0) / 1000
		# print("Speed in k/h:", kilometers_ph)
		entries[i+1].data['speed'] = kilometers_ph

	speed_sum = sum([x.data['speed'] for x in entries])
	avg_speed = speed_sum/float(len(entries))
	#print("The sum of speeds is", speed_sum)
	#print("Number of entries:", len(entries))
	#print("The average speed for this range of data is: {} kilometers per hour.".format(avg_speed))
	return entries
