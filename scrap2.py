from __future__ import print_function
import tempfile
import datetime
import json
from models import Bunch, segment, segment_series, geo_utils, time_utils
import app as whereis

import matplotlib
import matplotlib.pyplot as plt

from kalman_filter import kalman, coordinate

Coordinate = coordinate.Coordinate
KalmanFilter = kalman.KalmanFilter
SegmentSeries = segment_series.SegmentSeries


def xget(coord): return coord[0]
def yget(coord): return coord[0]
def min_max(coords, getter=lambda z: z, margin=100):
	return min(coords, key=getter)-margin, max(coords, key=getter)+margin

def increment_epoch_by_day(ts, count=1):
	# Adds the number of seconds in a day
	return ts + (count * 86400)

def main():
	init_time = Bunch(
		start="09:00:00 03-07-15",
		end=  "19:00:00 03-07-15"
	)
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)

	entries = []
	begin = increment_epoch_by_day(init_time.start, 0)
	end = increment_epoch_by_day(init_time.end, 5)
	
	series = SegmentSeries(whereis.AutoDB(), start_time=begin, stop_time=end)
	coords = series.xy_coords

	process_variance = 50
	estimated_measurement_variance = 500 # meters
	kf = KalmanFilter(process_variance, estimated_measurement_variance)
	adjusted_graph = []
	for c in coords:
		coord = Coordinate(c)
		kf.input_latest_noisy_measurement(coord)
		adjusted_graph.append(kf.get_latest_estimated_measurement())

	ylist, xlist = zip(*coords)
	xlist = [-n for n in xlist]

	adjusted_graph = [ [c.x, c.y] for c in adjusted_graph]
	cy, cx = zip(*adjusted_graph)
	cx = [-n for n in cx]
	#print(cx)
	#print(cy)

	fig, ax = plt.subplots()
	# plt.plot(xlist, ylist)
	ax.plot(cx, cy, 
		color='r',
		marker='o',
		markersize=0.25,
		markeredgewidth=0.05,
		linewidth=0.5
	
	)
	ax.plot(xlist, ylist,
		marker='o',
		markersize=0.25,
		markeredgewidth=0.05,
		linewidth=0.1,
	)
	ax.set_aspect('equal')
	print(min(cx + xlist), max(cx + xlist))
	ax.set_xlim(min(cx + xlist)-100, max(cx + xlist)+100)
	ax.set_ylim(min(cy + ylist)-100, max(cy + ylist)+100)

	#ax.set_xlim(*min_max(cx))
	#ax.set_ylim(*min_max(cy))

	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.get_xaxis().set_ticks([])
	ax.get_yaxis().set_ticks([])

	# plt.savefig('img.png')
	print('Writing image')
	fig.savefig('img.png', bbox_inches='tight', dpi=2000)








if __name__ == '__main__':
	main()
