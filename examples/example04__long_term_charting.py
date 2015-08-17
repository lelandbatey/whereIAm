"""

Gathers data from a very large time period and charts it all. Centers around
the greater Richland Area, cutting off travel to other locations.

"""

from __future__ import print_function
import sys
sys.path.append('../')
from models import Bunch, SegmentSeries, geo_utils, time_utils
import matplotlib.pyplot as plt
import app as whereis

#pylint: disable=W0312

def main():
	init_time = Bunch(\
	                  start="17:00:00 30-04-15",
	                  end="02:00:00 1-05-15"
	                 )
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)
	series = SegmentSeries(whereis.AutoDB(),
	                       start_time=init_time.start,
	                       stop_time=init_time.end,
	                       filter_outliers=True
	                       )
	moving = series.get_moving_segments()
	moving_coords = [[seg.x, seg.y] for seg in moving]
	motionless_coords = [[seg.x, seg.y] for seg in series.get_motionless_segments()]

	motx, moty = geo_utils.format_xy_matplotlib(motionless_coords)
	movx, movy = geo_utils.format_xy_matplotlib(moving_coords)
	xlist, ylist = geo_utils.format_xy_matplotlib(series.xy_coords)

	fig, ax = plt.subplots()

	ax.plot(xlist, ylist,
	        alpha=0.5,
	        marker='o',
	        markersize=0.2,
	        markeredgewidth=0.05,
	        linewidth=0.1,
	       )
	ax.plot(movx, movy, 'o',
	        color='yellow',
	        markersize=0.25,
	        markeredgewidth=0.05,
	       )
	ax.plot(motx, moty, 'o',
	        color='red',
	        markersize=0.25,
	        markeredgewidth=0.05,
	       )

	ax.set_aspect('equal')
	ax.set_xlim(-7500, 15000)
	ax.set_ylim(-12000, 4000)

	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.get_xaxis().set_ticks([])
	ax.get_yaxis().set_ticks([])

	print('Writing image')
	fig.savefig('example04__long_term_charting.png', bbox_inches='tight', dpi=2000)

if __name__ == '__main__':
	main()