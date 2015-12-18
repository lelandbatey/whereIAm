"""
Creates xy coordinates using a "Dead Reckoning" method, where each coordinate
is calculated with it's prior coordinate as it's anchor point. This is
susceptible to drifting data, something very noticeable in the generated
image.
"""

from __future__ import print_function
import sys
sys.path.append('../')

from models import Bunch, Segment, SegmentSeries, geo_utils, time_utils
import matplotlib.pyplot as plt
import app as whereis


#pylint: disable=W0312


def xget(coord): return coord[0]
def yget(coord): return coord[0]
def min_max(coords, getter, margin=100):
	return min(coords, key=getter)-margin, max(coords, key=getter)+margin

def increment_epoch_by_day(ts, count=1):
	"""Adds the number of seconds in a day.
	Useful for incrementing a given epoch timestamp by one day."""
	return ts + (count * 86400)

def main():

	init_time = Bunch(\
	                  start="08:59:00 02-07-15",
	                  end="19:00:00 02-07-15"
	                 )
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)

	entries = []
	begin = increment_epoch_by_day(init_time.start, 0)
	end = increment_epoch_by_day(init_time.end, 3)
	print('begin_UTC_Epoch:', begin)
	print('end_UTC_Epoch:', end)

	entries += whereis.AutoDB().get_date_range(begin, end)
	print('Retrieved entries from database')

	# entries = geo_utils.calculate_bearing(entries)
	print('Calculated bearing for all data')
	series = []

	for index in range(1, len(entries)):
	# for entry in entries:
		# When passed only an entry id, a Segment looks up the previous id and
		# uses that for it's starting entry. So if you pass an `id` for
		# `Entry_n`, it looks up `Entry_n-1` and uses that as it's starting
		# entry. The xy for the Segment is then calculated as xy for `Entry_n`
		# assuming `Entry_n-1` is the origin.
		#
		# Note also that this example runs extremely slowly since AutoDB
		# automatically creates and closes the database connection for every
		# query. So each segment means a new disk read.
		seg = Segment([entries[index-1], entries[index]], whereis.AutoDB())
		series.append(seg)
	print('Created segments')

	# Assembling all the xy coordinates via dead-reckoning
	coords = [[0, 0]]
	for i in range(len(series)):
		x = series[i].x
		y = series[i].y
		coords.append([x+coords[i][0], y+coords[i][1]])
	# coords = series.xy_coords
	print('Created xy coords')

	ylist, xlist = zip(*coords)
	xlist = [-n for n in xlist]

	fig, ax = plt.subplots()

	ax.plot(xlist, ylist,
	        marker='o',
	        markersize=0.25,
	        markeredgewidth=0.05,
	        linewidth=0.1,
	       )
	ax.set_aspect('equal')
	ax.set_xlim(*min_max(xlist, lambda x: x))
	ax.set_ylim(*min_max(ylist, lambda y: y))

	# Uncomment the below lines to hide the axis labels
	# ax.set_yticklabels([])
	# ax.set_xticklabels([])
	# ax.get_xaxis().set_ticks([])
	# ax.get_yaxis().set_ticks([])

	print('Writing image')
	fig.savefig('example00__dead_reckoning.png', bbox_inches='tight', dpi=2000)

if __name__ == '__main__':
	main()
