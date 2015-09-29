"""
Passes xy coordinates through a kalman filter to help approximate the location
of a given point.
"""

from __future__ import print_function
import sys
sys.path.append('../')

from models import Bunch, SegmentSeries, time_utils
from models.kalman_filter import KalmanFilter, Coordinate
import matplotlib.pyplot as plt
import app as whereis


#pylint: disable=W0312


def increment_epoch_by_day(ts, count=1):
	"""Adds the number of seconds in a day.
	Useful for incrementing a given epoch timestamp by one day."""
	return ts + (count * 86400)

def main():
	init_time = Bunch(\
	                  start="09:00:00 03-07-15",
	                  end="19:00:00 03-07-15"
	                 )
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)

	begin = increment_epoch_by_day(init_time.start, 0)
	end = increment_epoch_by_day(init_time.end, 5)
	print('begin_UTC_Epoch:', begin)
	print('end_UTC_Epoch:', end)
	
	series = SegmentSeries(whereis.AutoDB(), start_time=begin, stop_time=end)
	print("Built SegmentSeries from database.")
	coords = series.xy_coords

	process_variance = 50
	estimated_measurement_variance = 500 # meters
	klmn_fltr = KalmanFilter(process_variance, estimated_measurement_variance)
	adjusted_graph = []
	for rawcoord in coords:
		coord = Coordinate(rawcoord)
		klmn_fltr.input_latest_noisy_measurement(coord)
		adjusted_graph.append(klmn_fltr.get_latest_estimated_measurement())
	print("Finished filtering coordinates via KalmanFilter")

	ylist, xlist = zip(*coords)
	xlist = [-n for n in xlist]

	adjusted_graph = [[c.x, c.y] for c in adjusted_graph]
	kalmany, kalmanx = zip(*adjusted_graph)
	kalmanx = [-n for n in kalmanx]

	fig, ax = plt.subplots()

	ax.plot(kalmanx, kalmany, 
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
	ax.set_xlim(min(kalmanx + xlist)-100, max(kalmanx + xlist)+100)
	ax.set_ylim(min(kalmany + ylist)-100, max(kalmany + ylist)+100)
	
	# Uncomment the below lines to hide the axis labels 
	# ax.set_yticklabels([])
	# ax.set_xticklabels([])
	# ax.get_xaxis().set_ticks([])
	# ax.get_yaxis().set_ticks([])

	print('Writing image')
	fig.savefig('example01__kalman_filter.png', bbox_inches='tight', dpi=2000)


if __name__ == '__main__':
	main()
