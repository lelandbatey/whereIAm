from __future__ import print_function
import tempfile
import datetime
import json
from models import Bunch, segment, geo_utils, time_utils
import app as whereis

import matplotlib
import matplotlib.pyplot as plt


def xget(coord): return coord[0]
def yget(coord): return coord[0]
def min_max(coords, getter, margin=100):
	return min(coords, key=getter)-margin, max(coords, key=getter)+margin

def increment_epoch_by_day(ts, count=1):
	# Adds the number of seconds in a day
	return ts + (count * 86400)

def main():
	# Bounds for known good data starting on June 1st, 2015
	# begin = 1433199955
	# end = 1433206261

	# begin = 1432450800
	# end = 1435962671

	init_time = Bunch(
		start="09:00:00 02-07-15",
		end=  "19:00:00 02-07-15"
	)
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)

	entries = []
	begin = increment_epoch_by_day(init_time.start, 0)
	end = increment_epoch_by_day(init_time.end, 3)
	print('begin:', begin)
	print('end:', end)
	# 1435962671
	entries += whereis.AutoDB().get_date_range(begin, end)

	print('Retrieved entries from database')
	entries = geo_utils.calculate_bearing(entries)
	print('Calculated bearing for all data')
	series = []

	for entry in entries:
		seg = segment.Segment(entry['id'], whereis.AutoDB())
		series.append(seg)
	print('Created segments')
	coords = [[0,0]]
	for i in range(len(series)):
		# print(series[i].bearing)
		x = series[i].x
		y = series[i].y
		coords.append([x+coords[i][0], y+coords[i][1]])
	print('Created xy coords')

	ylist, xlist = zip(*coords)
	xlist = [-n for n in xlist]

	fig, ax = plt.subplots()
	# plt.plot(xlist, ylist)
	ax.plot(xlist, ylist,
		marker='o',
		markersize=0.25,
		markeredgewidth=0.05,
		linewidth=0.1,
	)
	ax.set_aspect('equal')
	ax.set_xlim(*min_max(xlist, lambda x: x))
	ax.set_ylim(*min_max(ylist, lambda y: y))

	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.get_xaxis().set_ticks([])
	ax.get_yaxis().set_ticks([])

	# plt.savefig('img.png')
	print('Writing image')
	fig.savefig('img.png', bbox_inches='tight', dpi=2000)








if __name__ == '__main__':
	main()
