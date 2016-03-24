"""
Tries to identify groups of moving entries by looking at consecutive entries
that are beyond a certain threshold of speed.
"""

from __future__ import print_function
import datetime as dt
from itertools import chain
import sys

sys.path.append('../')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from app.models import time_utils, geo_utils
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

        ts0 = self.first['monotonic_timestamp']
        ts1 = self.last['monotonic_timestamp']
        self.mean_timestamp = (ts0 + ts1) / 2.0


def main():
    start_time = "09:00:00 03-07-15"
    stop_time = "19:00:00 06-07-15"

    start_time = time_utils.simplefmt_in_pdt_to_utc_epoch(start_time)
    stop_time = time_utils.simplefmt_in_pdt_to_utc_epoch(stop_time)
    print('begin_UTC_Epoch:', start_time)
    print('end_UTC_Epoch:', stop_time)

    # Gather entries from database, transform into segments
    entries = whereis.AutoDB().get_date_range(start_time, stop_time)
    segments = []
    for idx in range(1, len(entries)):
        tmp_seg = Segment(entries[idx-1], entries[idx])
        segments.append(tmp_seg)
    # Make sure that the correct number of segments have been created for the
    # amount of entries
    assert len(segments) == (len(entries) - 1)
    print("Created '{}' segments from entries".format(len(segments)))

    speeds = [s.speed for s in segments]
    filt_speeds = geo_utils.median_filter(speeds, winlen=5)
    # Ensure that we have a correct number of filtered speed values
    assert len(filt_speeds) == len(segments)

    # Find all the segments that are "moving", defined as having a speed above
    # 1 meter per second. Instead of using the raw speeds, check against the
    # filtered speeds. Additionally, a segment can only count as "moving" if it
    # is part of a series of at least 3 segments that satisfy all other
    # criteria for "moving".
    moving_segs = []
    tmp_moving_segs = []
    for idx, speed in enumerate(filt_speeds):
        if speed >= 1.0 and speed <= 1000:
            tmp_moving_segs.append(segments[idx])
        elif len(tmp_moving_segs) < 3:
            del tmp_moving_segs
            tmp_moving_segs = []
        elif len(tmp_moving_segs) > 2:
            moving_segs.append(tmp_moving_segs)
            del tmp_moving_segs
            tmp_moving_segs = []
    print("Found all '{}' segments which represent movement".format(len(moving_segs)))

    to_dt = dt.datetime.fromtimestamp
    series_ts = [to_dt(s.mean_timestamp) for s in segments]
    moving_ts = [to_dt(s.mean_timestamp) for s in chain.from_iterable(moving_segs)]

    print("Time difference of series: {} - {} = {}".format(max(series_ts), min(series_ts), max(series_ts) - min(series_ts)))

    fig, ax = plt.subplots()

    ax.plot(series_ts, speeds, color='blue')
    ax.plot(series_ts, filt_speeds, color='green')
    ax.plot(moving_ts, [0 for _ in moving_ts], 'o', color='yellow')

    ax.set_ylim(min(speeds)-2, 50)

    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    date_formatter = mdates.DateFormatter("%m-%d %H:%M")
    ax.xaxis.set_major_formatter(date_formatter)

    print("Writing image")
    fig.set_size_inches(240, 14)
    fig.savefig('example02__speed_threshold.png',
                bbox_inches='tight',
                dpi=100
               )

    # To get an interactive version of this graph, comment out the two lines
    # after "writing image" then uncomment the below line.
    # plt.show()



if __name__ == "__main__":
    main()
