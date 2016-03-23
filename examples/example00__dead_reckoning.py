"""
Creates xy coordinates using a "Dead Reckoning" method, where each coordinate
is calculated with it's prior coordinate as it's anchor point. This is
susceptible to drifting data, something very noticeable in the generated
image.
"""

from __future__ import print_function
from itertools import izip
import math
import sys

import matplotlib.pyplot as plt

sys.path.append('../')
from app.models import geo_utils, time_utils
import app.frontend as whereis


#pylint: disable=W0312


def min_max(coords, getter, margin=100):
    return min(coords, key=getter)-margin, max(coords, key=getter)+margin

def increment_epoch_by_day(ts, count=1):
    """Adds the number of seconds in a day.
    Useful for incrementing a given epoch timestamp by one day."""
    return ts + (count * 86400)

def main():

    start_time = "08:59:00 02-07-15"
    stop_time = "19:00:00 02-07-15"

    start_time = time_utils.simplefmt_in_pdt_to_utc_epoch(start_time)
    stop_time = time_utils.simplefmt_in_pdt_to_utc_epoch(stop_time)


    entries = []
    begin = increment_epoch_by_day(start_time, 0)
    end = increment_epoch_by_day(stop_time, 3)
    print('begin_UTC_Epoch:', begin)
    print('end_UTC_Epoch:', end)

    entries += whereis.AutoDB().get_date_range(begin, end)
    print('Retrieved entries from database')

    # Calculate the bearing for each "segment" (a segment represents the line
    # between two coordinates)
    seg_bearings = []
    for idx in range(1, len(entries)):
        bearing = geo_utils.calculate_bearing(entries[idx-1], entries[idx])
        seg_bearings.append(bearing)
    print('Calculated bearing for each segment')

    # Calculate the length of each segment
    seg_lengths = []
    for idx in range(1, len(entries)):
        ent0, ent1 = entries[idx-1], entries[idx]
        linear_length = geo_utils.distance_on_unit_sphere(ent0['latitude'], ent0['longitude'], ent1['latitude'], ent1['longitude'])
        linear_length = linear_length * 6378100
        seg_lengths.append(linear_length)
    print('Calculated length of each segment')

    # The length of calculated attributes of segments should be the same, and
    # both should equal the the number of segments derivable from the list of
    # entries, which would be length(entries) - 1
    assert len(seg_bearings) == len(seg_lengths) == (len(entries) - 1)

    # Extrapolate x/y coords from length and bearing of each segment in a
    # process called "dead reckoning"
    coords = [[0, 0]]
    for bearing, length in izip(seg_bearings, seg_lengths):
        x = length * math.cos(bearing)
        y = length * math.sin(bearing)
        priorx, priory = coords[-1]
        coords.append([x+priorx, y+priory])
    print("Extrapolated x/y coordinates from calculated segment data.")


    ylist, xlist = zip(*coords)
    # xlist = [-n for n in xlist]

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
