#!/usr/bin/env python

"""Unit tests for whereis."""

from __future__ import print_function
import unittest
import tempfile
import os.path
import json
import sys
import os
sys.path.append('../')

import app as whereis
#pylint: disable=W0312
#pylint: disable=C0330

def a_subset_b(a, b):
	"""Returns true if the value of all keys in a are equivelent to the value of
	those same keys in b."""
	for thing in a:
		if a[thing] != b[thing]:
			return False
	return True

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
		# print(cur_pos)
		assert a_subset_b(whereis.SEED_DATA, cur_pos)

	def test_add_entry(self):
		"""Add new data to the database, then verify that it's correctly entered."""
		new_data = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:00:00.00Z"
		}
		self.app.post('/update', data=new_data)
		cur_pos = self.app.get('/currentpos')
		cur_pos = json.loads(cur_pos.data)
		assert a_subset_b(new_data, cur_pos)
	
	def test_add_single(self):
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





if __name__ == '__main__':
	unittest.main()
