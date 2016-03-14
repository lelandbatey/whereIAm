from __future__ import print_function
from sqlalchemy import create_engine
import geo_utils
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

	@property
	def json(self):
		"""Returns json object representation of object."""
		to_return = json.loads(self.raw_request)
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
		self.latest_epoch = 0
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
		if self.latest_epoch and entry.monotonic_timestamp < self.latest_epoch:
			print("Entry was received after another entry with a later timestamp.")
			print('Entry:{} latest:{}'.format(entry.monotonic_timestamp, self.latest_epoch))
		else:
			self.latest_epoch = entry.monotonic_timestamp
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
		).order_by(LocationEntry.monotonic_timestamp)
		to_return = [x for x in entries]
		to_return = [x.json for x in to_return]
		return to_return

	def get_latest(self):
		"""Returns the latest LocationEntry which has been added to the db."""
		entry = self.session.query(LocationEntry)\
		            .order_by(LocationEntry.id_num.desc())\
		            .first()
		if entry:
			return entry.json
		else:
			return entry

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
		).order_by(LocationEntry.monotonic_timestamp)
		to_return = [x for x in entries]
		to_return = [x.json for x in to_return]
		return to_return

	def get_time(self, ent_time):
		"""Returns the entry with the time closest to the given time"""
		query = self.session.query(LocationEntry).order_by(
			"abs(monotonic_timestamp - {})".format(ent_time)
		)
		#print(str(query.statement.compile()))
		entry = query.first()
		return entry.json


