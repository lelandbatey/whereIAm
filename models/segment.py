from __future__ import print_function
import entry_model
import geo_utils
import math

from . import Bunch



class Segment(object):
	def __init__(self, index, model):
		self.index = index
		begin = model.get_id(index-1)
		end = model.get_id(index)
		self.start, self.stop = geo_utils.calculate_bearing([begin, end])
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
		self.speed = geo_utils.get_speed(self.start, self.stop)
		self.x = self.linear_length * math.cos(self.bearing)
		self.y = self.linear_length * math.sin(self.bearing)

