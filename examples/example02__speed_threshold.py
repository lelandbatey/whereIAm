"""
Tries to identify groups of moving entries by looking at consecutive entries
that are beyond a certain threshold of speed.
"""

from __future__ import print_function
import sys

sys.path.append('../')

import matplotlib.pyplot as plt

from app.models import SegmentSeries, time_utils, geo_utils
import app.frontend as whereis

#pylint: disable=W0312


class Segment(object):
    """Represents data about the line-segment between two GPS coordinates."""
    def __init__(self, first_entry, last_entry):
        """Initialize the coordinates which define this Segment, as well as
        this Segments `bearing` (in radians from North), `linear_length` (in
        meters), and `speed` (in meters per second)."""
        self.first = first_entry
        self.last = last_entry

        self.bearing = geo_utils.calculate_bearing(self.first, self.last)

        arc_distance = geo_utils.distance_on_unit_sphere(
                self.first['latitude'], self.first['longitude'],
                self.last['latitude'], self.last['latitude']
                )
        # Multiply the arc-length by the radius of the earth in meters to get
        # the length in meters
        self.linear_length = arc_distance * 6378100

        self.speed = geo_utils.get_speed(self.first, self.last)


def main():
    start_time = "09:00:00 03-07-15"
    stop_time = "19:00:00 06-07-15"

    start_time = time_utils.simplefmt_in_pdt_to_utc_epoch(start_time)
    stop_time = time_utils.simplefmt_in_pdt_to_utc_epoch(stop_time)

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
