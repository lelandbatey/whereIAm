"""
Attempts to identify groups of moving entries by looking at consecutive
entries that are above a certain threshold of speed. 

Entries that are "moving" are marked with a yellow dot, while "motionless"
entries are marked with a red dot.
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
	                  start="09:00:00 01-04-15",
	                  end="19:00:00 23-04-15"
	                 )
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)
	series = SegmentSeries(whereis.AutoDB(),
	                       start_time=init_time.start,
	                       stop_time=init_time.end,
	                       filter_outliers=True
	                       )
	moving = series.get_all_moving_segments()
	moving_coords = [[seg.x, seg.y] for seg in moving]
	motionless_coords = [[seg.x, seg.y] for seg in series.get_all_motionless_segments()]

	motx, moty = geo_utils.format_xy_matplotlib(motionless_coords)
	movx, movy = geo_utils.format_xy_matplotlib(moving_coords)
	xlist, ylist = geo_utils.format_xy_matplotlib(series.xy_coords)

	fig, ax = plt.subplots()

	ax.plot(xlist, ylist,
	        alpha=0.5,
	        marker='o',
	        markersize=0.25,
	        markeredgewidth=0.05,
	        linewidth=0.1,
	       )
	ax.plot(movx, movy, 'o',
	        color='yellow',
	        markersize=0.5,
	        markeredgewidth=0.05,
	       )
	ax.plot(motx, moty, 'o',
	        color='red',
	        markersize=0.25,
	        markeredgewidth=0.05,
	       )

	ax.set_aspect('equal')
	ax.set_xlim(min(movx + xlist)-100, max(movx + xlist)+100)
	ax.set_ylim(min(movy + ylist)-100, max(movy + ylist)+100)

	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.get_xaxis().set_ticks([])
	ax.get_yaxis().set_ticks([])

	print('Writing image')
	fig.savefig('example03__highlight_moving.png', bbox_inches='tight', dpi=2000)


if __name__ == "__main__":
	main()


