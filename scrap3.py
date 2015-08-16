from __future__ import print_function
from models import Bunch, SegmentSeries, geo_utils, time_utils
import app as whereis

import matplotlib.pyplot as plt


def main():
	init_time = Bunch(
		start="09:00:00 03-07-15",
		end="19:00:00 06-07-15"
	)
	init_time.set_in_place(time_utils.simplefmt_in_pdt_to_utc_epoch)
	series = SegmentSeries(whereis.AutoDB(), start_time=init_time.start, stop_time=init_time.end)
	moving_ids = series.get_moving_ids()

	plt.plot(series.ids, series.speeds, color='blue')
	plt.plot(series.ids, series.get_filtered_speeds(5), color='green')
	plt.plot(moving_ids, [0 for _ in moving_ids], 'o', color='yellow')
	plt.show()



if __name__ == "main":
	main()
