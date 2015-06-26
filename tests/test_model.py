#!/usr/bin/env python

"""Unit tests for geo model."""

from __future__ import print_function
import unittest
import tempfile
import os.path
import random
import sys
import os
sys.path.append('../')

import app as whereis
import geo_model
#pylint: disable=W0312
#pylint: disable=C0330

def a_subset_b(a, b):
	for thing in a:
		if a[thing] != b[thing]:
			return False
	return True

def generate_entries(count=5):
	"""Generates entries with random data."""
	def rdgt(): return str(random.randint(1, 9))
	for _ in range(0, count):
		yield {
			"latitude": str(random.random()*100),
			"longitude": str(random.random()*100),
			"time": "201"+rdgt()+"-0"+rdgt()+"-01T0"+rdgt()+":00:00.00Z"
		}

class GeoModelUnitTests(unittest.TestCase):
	"""Tests the update backend for the app."""
	
	def setUp(self):
		"""Initialization of this group of tests."""
		self.seed_data = whereis.SEED_DATA
		self.db_fd, self.db_path = tempfile.mkstemp()
		# Creates the database, seeds it with initial data.
		self.model = geo_model.LocationModel(self.db_path)
		self.model.add_if_empty(self.seed_data)

	def tearDown(self):
		"""Cleanup for these unit tests."""
		os.close(self.db_fd)
		self.model.session.close()
		os.remove(self.db_path)
		# while True:
		# 	try:
		# 		break
		# 	except:
		# 		pass

	def test_check_new(self):
		"""Tests that the initial database contains the seed data."""
		assert a_subset_b(self.seed_data, self.model.get_latest())

	def test_add_single_entry(self):
		"""Tests adding a single new entry."""
		new_data = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2010-01-01T12:00:00.00Z"
		}
		self.model.new_entry(new_data)
		assert a_subset_b(new_data, self.model.get_latest())

	def test_add_several_entries(self):
		"""Tests that entries come back with correct data and in order."""
		new_data = [_ for _ in generate_entries()]
		for ent in new_data:
			self.model.new_entry(ent)
		new_data = [self.seed_data] + new_data
		tmp = self.model.get_all()
		# print(whereis.jdump(new_data))
		# print(whereis.jdump(tmp))
		for indx, val in enumerate(new_data):
			assert a_subset_b(new_data[indx], tmp[indx])

if __name__ == '__main__':
	unittest.main()

