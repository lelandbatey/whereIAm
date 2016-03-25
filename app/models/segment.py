from __future__ import print_function
import numbers
import math

from .. import geo_utils
import entry_model
from . import Bunch



class Segment(object):
	def __init__(self, index, model):
		begin, end = None, None
		if isinstance(index, numbers.Real):
			self.index = index
			begin = model.get_id(index-1)
			end = model.get_id(index)
		else:
			self.index = index[1]['id']
			begin = index[0]
			end = index[1]
		self.start, self.stop = geo_utils.calculate_bearing([begin, end])
		self.begin, self.end = self.start, self.stop
		self.start, self.stop = Bunch(**self.start), Bunch(**self.stop)
		# Multiplies distance as arc-length by the radius of the earth in
		# meters to get the length in meters
		self.linear_length = geo_utils.distance_on_unit_sphere(
			self.start.latitude,
			self.start.longitude,
			self.stop.latitude,
			self.stop.longitude,
		) * 6378100
		self.bearing = float(self.stop.derived_bearing)
		self.time_dist = self.stop.monotonic_timestamp - self.start.monotonic_timestamp
		assert not self.time_dist < 0.0, "start: {} {}, end: {} {}".format(self.begin['id'], self.start.monotonic_timestamp, self.end['id'], self.stop.monotonic_timestamp)
		self.speed = geo_utils.get_speed(self.start, self.stop)
		assert not self.speed < 0.0
		#self.x = (180 + float(self.start.longitude)) / 360
		#self.y = (90 - float(self.start.latitude)) / 180
		self.x = self.linear_length * math.cos(self.bearing)
		self.y = self.linear_length * math.sin(self.bearing)

	def json(self):
		return {
				'begin': self.begin,
				'end': self.end,
				'linear_length': self.linear_length,
				'bearing': self.bearing,
				'speed': self.speed,
				'x': self.x,
				'y': self.y
				}

	def __repr__(self):
		return str(self.json())

