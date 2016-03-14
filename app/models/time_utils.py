from __future__ import print_function
import time
import datetime


# Test

def simplefmt_in_pdt_to_utc_epoch(moment):
	"""Converts simple format string as if taken in PDT to UTC.

	This function is good for helping a developer in PDT query times in a
	format they're comfortable with.
	"""
	t = simplefmt_to_datetime(moment)
	# Add 7 hours 
	t += datetime.timedelta(0, 25200)
	return datetime_to_epoch(t)


def datetime_to_oddformat(moment):
	"""Converts datetime object to format %Y-%m-%dT%H:%M:%S.%fZ"""
	return datetime.datetime.strftime(moment, "%Y-%m-%dT%H:%M:%S.%fZ")
def oddformat_to_datetime(odd):
	"""Converts string in %Y-%m-%dT%H:%M:%S.%fZ to datetime"""
	return datetime.datetime.strptime(odd, "%Y-%m-%dT%H:%M:%S.%fZ")


def simplefmt_to_datetime(moment):
	"""Converts string in %H:%M:%S %d-%m-%y to datetime"""
	return datetime.datetime.strptime(moment, "%H:%M:%S %d-%m-%y")


def epoch_to_datetime(epoch):
	"""Converts an epoch timestamp to datetime."""
	return datetime.datetime.fromtimestamp(epoch)

def datetime_to_epoch(indate):
	"""Converts a datetime object to an epoch timestamp."""
	return (indate - datetime.datetime(1970, 1, 1)).total_seconds()
