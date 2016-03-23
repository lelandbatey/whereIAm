"""
Passes xy coordinates through a kalman filter to help approximate the location
of a given point.
"""

from __future__ import print_function
import sys
sys.path.append('../')

import matplotlib.pyplot as plt

from app.models import SegmentSeries, time_utils
from app.models.kalman_filter import KalmanFilter, Coordinate
import app.frontend as whereis


#pylint: disable=W0312


def increment_epoch_by_day(ts, count=1):
    """Adds the number of seconds in a day.
    Useful for incrementing a given epoch timestamp by one day."""
    return ts + (count * 86400)

def main():

    start_time = "09:00:00 03-07-15"
    stop_time = "19:00:00 03-07-15"

    start_time = time_utils.simplefmt_in_pdt_to_utc_epoch(start_time)
    stop_time = time_utils.simplefmt_in_pdt_to_utc_epoch(stop_time)


    begin = increment_epoch_by_day(start_time, 0)
    end = increment_epoch_by_day(stop_time, 5)
    print('begin_UTC_Epoch:', begin)
    print('end_UTC_Epoch:', end)

    # Gather coordinate data from lat-long
    entries = whereis.AutoDB().get_date_range(begin, end)
    coords = [[float(ent['latitude']), float(ent['longitude'])] for ent in entries]

    # Process coordinates using Kalman Filter
    process_variance = 0.006
    estimated_measurement_variance = 0.0005
    klmn_fltr = KalmanFilter(process_variance, estimated_measurement_variance)
    adjusted_graph = []
    for rawcoord in coords:
        coord = Coordinate(rawcoord)
        klmn_fltr.input_latest_noisy_measurement(coord)
        adjusted_graph.append(klmn_fltr.get_latest_estimated_measurement())
    print("Finished filtering coordinates via KalmanFilter")

    ylist, xlist = zip(*coords)

    adjusted_graph = [[c.x, c.y] for c in adjusted_graph]
    kalmany, kalmanx = zip(*adjusted_graph)

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
    ax.set_xlim(min(xlist)-0.001, max(xlist)+0.001)
    ax.set_ylim(min(ylist)-0.001, max(ylist)+0.001)

    # Uncomment the below lines to hide the axis labels
    # ax.set_yticklabels([])
    # ax.set_xticklabels([])
    # ax.get_xaxis().set_ticks([])
    # ax.get_yaxis().set_ticks([])

    print('Writing image')
    fig.savefig('example01__kalman_filter.png', bbox_inches='tight', dpi=2000)


if __name__ == '__main__':
    main()
