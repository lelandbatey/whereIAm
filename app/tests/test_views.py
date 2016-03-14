#!/usr/bin/env python

"""Unit tests for whereis."""

from __future__ import print_function
import unittest
import tempfile
import datetime
import os.path
import random
import json
import os

from .. import frontend as whereis
#pylint: disable=W0312
#pylint: disable=C0330

def a_subset_b(a, b):
	"""Returns true if the value of all keys in a are equivelent to the value of
	those same keys in b."""
	for thing in a:
		if a[thing] != b[thing]:
			return False
	return True

def datetime_to_epoch(indate):
	"""Converts a datetime object to an epoch timestamp."""
	return (indate - datetime.datetime(1970, 1, 1)).total_seconds()

def too_oddformat(moment):
	return datetime.datetime.strftime(moment, "%Y-%m-%dT%H:%M:%S.%fZ")
def from_oddformat(odd):
	return datetime.datetime.strptime(odd, "%Y-%m-%dT%H:%M:%S.%fZ")


def create_test_entries(count=1):
	starttime = from_oddformat("2010-01-01T12:00:00.00Z")

	def base_data(k):
		return {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:{:0>2}:00.00Z".format(k)
		}
	rv = []
	if count > 1:
		rv = [base_data(x) for x in range(0, count)]
	else:
		rv = base_data(0)
	return rv



class WhereisUnitTests(unittest.TestCase):
	"""Tests the update endpoint of app."""
	
	def setUp(self):
		"""Initialization of this group of tests."""
		self.db_fd, whereis.APP.config['DATABASE'] = tempfile.mkstemp()
		self.log_fd, whereis.APP.config['LOG_FILE_PATH'] = tempfile.mkstemp()
		# print(os.path.abspath(whereis.APP.config['DATABASE']))
		whereis.APP.config['TESTING'] = True
		self.app = whereis.APP.test_client()
		# This has the side effect of creating our database if it doesn't already exist.
		self.model = whereis.get_db()
	
	def tearDown(self):
		"""Cleanup for these unit tests."""
		self.model.session.close()
		os.close(self.db_fd)
		os.remove(whereis.APP.config['DATABASE'])
		os.close(self.log_fd)
		os.remove(whereis.APP.config['LOG_FILE_PATH'])

	def test_empty_db(self):
		"""With a fresh and empty database, ensure that the seed data is still present."""
		cur_pos = self.app.get('/currentpos')
		cur_pos = json.loads(cur_pos.data)
		assert a_subset_b(whereis.SEED_DATA, cur_pos)

	def test_add_entry(self):
		"""Add new data to the database, then verify that it's correctly entered."""
		new_data = create_test_entries()
		self.app.post('/update', data=new_data)
		cur_pos = self.app.get('/currentpos')
		cur_pos = json.loads(cur_pos.data)
		assert a_subset_b(new_data, cur_pos)
	
	def test_add_single_entry(self):
		"""Add a single entry, ensure that it's the only entry (aside from the seed data)."""
		new_data = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:00:00.00Z"
		}
		self.app.post('/update', data=new_data)
		cur_pos = self.app.get('/currentpos')
		cur_pos = json.loads(cur_pos.data)
		# Sqlite indexing starts with 1, so the second entry has an id of 2.
		assert cur_pos['id'] == 2

	def test_verify_get_ids(self):
		"""Adds several entries, verifies they are correctly orderd."""
		new_data = create_test_entries(10)
		for d in new_data:
			self.app.post('/update', data=d)
		for x in range(0, len(new_data)):
			cur_ent = self.app.get('/entry/id/'+str(x+2))
			cur_ent = json.loads(cur_ent.data)
			assert a_subset_b(new_data[x], cur_ent)

	def test_verify_get_id_range(self):
		"""Add then get several entries in order."""
		new_data = create_test_entries(15)
		for d in new_data:
			self.app.post('/update', data=d)
		latest = json.loads(self.app.get('/entry').data)
		entry_array = json.loads(self.app.get('/entry/id/2/{}'.format(latest['id'])).data)
		for index, _ in enumerate(entry_array):
			assert a_subset_b(new_data[index], entry_array[index])

	def test_verify_get_time(self):
		"""Check that looking up by time returns nearest time"""
		one = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:01:00.00Z"
		}
		two = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:01:45.00Z"
		}
		self.app.post('/update', data=one)
		self.app.post('/update', data=two)
		epoch = int(datetime_to_epoch(from_oddformat(one['time']))) 
		t = '/entry/time/{}'.format(epoch + 30)
		entry = self.app.get(t)
		assert a_subset_b(two, json.loads(entry.data))

	def test_verify_get_time_range(self):
		"""Check that querying by time range returns entries within bounds."""
		new_data = create_test_entries(15)
		for d in new_data:
			self.app.post('/update', data=d)
		def get_epoch(val): return int(datetime_to_epoch(from_oddformat(val['time'])))
		first, last = new_data[0], new_data[-1]
		first, last = get_epoch(first), get_epoch(last)
		first += 1
		last -= 1
		query_str = '/entry/time/{}/{}'.format(first, last)
		entries = json.loads(self.app.get(query_str).data)
		good_range = new_data[1:-1]

		assert len(entries) == len(good_range)
		for index, _ in enumerate(good_range):
			assert a_subset_b(good_range[index], entries[index])






if __name__ == '__main__':
	unittest.main()
