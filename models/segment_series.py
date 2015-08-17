from __future__ import print_function
import geo_utils
from segment import Segment


class SegmentSeries(object):
	"""A series of segments and data about those segments."""
	def __init__(self,
	             model,
	             entries=None,
	             start_time=None,
	             stop_time=None,
	             start_id=None,
	             stop_id=None,
	             filter_outliers=False
	            ):

		self.entries = entries
		self.model = model

		if not self.entries:
			if start_time and stop_time:
				self.entries = self.model.get_date_range(start_time, stop_time)
			elif start_id and stop_id:
				self.entries = self.model.get_id_range(start_id, stop_id)
		self.entries = geo_utils.calculate_bearing(self.entries)

		self._init_segments()
		if filter_outliers:
			self._filter_bad()
		self._init_xy_coords()
		self._init_speeds()
		self.ids = [ent['id'] for ent in self.entries[1:]]

	def _init_segments(self):
		self.segments = []
		for index in range(1, len(self.entries)):
			#print(self.entries[index])
			seg = Segment([self.entries[index-1], self.entries[index]], self.model)
			self.segments.append(seg)

	def _init_xy_coords(self):
		self.xy_coords = [[0, 0]]
		temp_segs = []
		for ent in self.entries[1:]:
			temp_segs.append(Segment([self.entries[0], ent], self.model))
		for seg in temp_segs:
			self.xy_coords.append([seg.x, seg.y])
		for index in range(len(temp_segs)):
			self.segments[index].x = temp_segs[index].x
			self.segments[index].y = temp_segs[index].y
		del temp_segs

	def _init_speeds(self):
		self.speeds = [seg.speed for seg in self.segments]
	
	def _filter_bad(self):
		"""Removes entries that are outliers in terms of speed."""
		bad_entries = []
		winlen = 7
		middle = winlen//2

		for seg in range(0, len(self.segments)):
			sel = geo_utils.get_candidates(self.segments, seg, winlen)
			pre = sel[:middle]
			post = sel[middle+1:]
			mid = sel[middle]
			pre_mean = geo_utils.mean(pre, lambda x: max(1, x.speed))
			post_mean = geo_utils.mean(post, lambda x: max(1, x.speed))
			if mid.speed > (20*pre_mean) or \
			   mid.speed > (20*post_mean) or \
			   mid.speed > 260:
				bad = None
				for ent in self.entries:
					if mid.end['id'] == ent['id']:
						bad = self.entries.index(ent)
				if bad == None:
					raise Exception("How could we not find the index if we found the object?!")
				bad_entries.append(bad)
				#del self.entries[bad]
				# print('sel:', [s.speed for s in sel])
				# print("pre:", [p.speed for p in pre])
				# print("post:", [p.speed for p in post])
				# print('mid:', mid.speed)
				# print('bad:', self.segments[bad-1].speed)
				# print("cur/total: {} / {}".format(seg, len(self.segments)))
				#self._init_segments()
				#self._filter_bad()
				#return
		delcount = 0
		for bent in bad_entries:
			bent = bent-delcount
			# print([s.speed for s in self.segments[delcount+bent-5:delcount+bent+5]])
			# print("speed:", self.segments[delcount+bent-1].speed)
			assert self.entries[bent] == self.segments[delcount+bent-1].end
			del self.entries[bent]
			delcount += 1
		self._init_segments()


	def get_filtered_speeds(self, winlen=3):
		medians = geo_utils.median_filter(self.speeds, winlen)
		assert len(medians) == len(self.ids), "medians count: {}, ids count: {}".format(len(medians), len(self.ids))
		return medians

	def get_moving_ids(self):
		return [seg.index for seg in self.get_moving_segments()]
	
	def get_moving_segments(self):
		return self.get_segments_by_speed(1, 1000)

	def get_motionless_segments(self):
		return self.get_segments_by_speed(-1, 0.99999)

	def get_segments_by_speed(self, minspeed, maxspeed):
		segments = []
		speeds = self.get_filtered_speeds(winlen=5)
		tmp = []
		for index, speed in enumerate(speeds):
			if speed >= minspeed and speed <= maxspeed:
				tmp.append(self.segments[index])
			elif len(tmp) < 3:
				del tmp
				tmp = []
			if len(tmp) > 2:
				segments += tmp
				del tmp
				tmp = []
		return segments




