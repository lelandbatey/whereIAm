import geo_utils

class Bunch(object):
	def __init__(self, **kwds):
		self.__dict__.update(kwds)
	def set_in_place(self, func):
		for v in self.__dict__.keys():
			self.__dict__[v] = func(self.__dict__[v])


from segment_series import SegmentSeries
from segment import Segment

