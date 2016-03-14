#!/usr/bin/env python

"""Unit tests for geo model."""

from __future__ import print_function
import unittest
import tempfile
import os.path
import random
import os

from .. import frontend as whereis
from ..models import entry_model, time_utils

#pylint: disable=W0312
#pylint: disable=C0330

def a_subset_b(a, b):
	for thing in a:
		if a[thing] != b[thing]:
			return False
	return True

def generate_entries(count=5):
	"""Generates entries with deterministically random data."""
	random.seed(1)
	# Fri, 01 Jan 2015 12:00:00 GMT
	start_time = 1420113600

	# A point in the scrubby desert near the bottom of Washington State
	init_lat = 46.0
	init_long = -120.0

	# About one quarter mile
	delta = 0.0005

	rtime = start_time
	rlat = init_lat
	rlon = init_long
	for _ in range(0, count):
		yield {
			"latitude": str(rlat),
			"longitude": str(rlon),
			"time": time_utils.datetime_to_oddformat(time_utils.epoch_to_datetime(rtime))
		}
		rlat += delta
		rlon -= delta
		rtime += 60


class GeoModelUnitTests(unittest.TestCase):
	"""Tests the update backend for the app."""
	
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
	
	def test_add_new_entry(self):
		"""Tests addition of five standard entries."""
		entries = [ _ for _ in generate_entries(5)]
		for ent in entries:
			self.model.new_entry(ent)
		for idx in range(0, len(entries)):
			epc_time = time_utils.datetime_to_epoch(time_utils.oddformat_to_datetime(entries[idx]['time']))
			ent = self.model.get_time(epc_time)
			assert a_subset_b(entries[idx], ent)

	def test_seed(self):
		"""Tests that the initial database contains the seed data."""
		assert a_subset_b(whereis.SEED_DATA, self.model.get_latest())

	def test_add_single_entry(self):
		"""Tests adding a single new entry."""
		new_data = {
			"latitude": "0.0",
			"longitude": "0.0",
			"time": "2015-01-01T12:00:00.00Z"
		}
		self.model.new_entry(new_data)
		assert a_subset_b(new_data, self.model.get_latest())

if __name__ == '__main__':
	unittest.main()

