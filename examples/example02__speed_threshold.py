"""
Tries to identify groups of moving entries by looking at consecutive entries
that are beyond a certain threshold of speed. 
"""

from __future__ import print_function
import sys
sys.path.append('../')
from models import Bunch, SegmentSeries, time_utils
import matplotlib.pyplot as plt
import app as whereis

#pylint: disable=W0312

def main():
	init_time = Bunch(\
	                  start="09:00:00 03-07-15",
	                  end="19:00:00 06-07-15"
	                 )
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)
	series = SegmentSeries(whereis.AutoDB(), start_time=init_time.start, stop_time=init_time.end)
	moving_ids = series.get_moving_ids()

	fig, ax = plt.subplots()

	ax.plot(series.ids, series.speeds, color='blue')
	ax.plot(series.ids, series.get_filtered_speeds(5), color='green')
	ax.plot(moving_ids, [0 for _ in moving_ids], 'o', color='yellow')

	ax.set_aspect('equal')
	ax.set_xlim(min(series.ids)-5, max(series.ids)+5)
	ax.set_ylim(min(series.speeds)-10, max(series.speeds)+10)

	print("Writing image")
	fig.set_size_inches(240, 28.5866)
	fig.savefig('example02__speed_threshold.png',
	            bbox_inches='tight',
	            dpi=100
	           )

	# To get an interactive version of this graph, comment out the two lines
	# after "writing image" then uncomment the below line.
	# plt.show()



if __name__ == "__main__":
	main()
