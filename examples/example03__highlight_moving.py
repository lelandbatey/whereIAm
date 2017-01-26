"""
Attempts to identify groups of moving entries by looking at consecutive
entries that are above a certain threshold of speed.

Entries that are "moving" are marked with a yellow dot, while "motionless"
entries are marked with a red dot.
"""
from __future__ import print_function
from itertools import chain
import sys

import matplotlib.pyplot as plt

sys.path.append('../')

from app.models import SegmentSeries
from app import frontend as whereis
from app import geo_utils, time_utils



def designate_moving_segments(segments, filt_speeds):
    """Returns two lists, each which contains multiple lists of Segments. The
    first return value is the list of groups of moving Segments, the second is
    the list of groups of motionless Segments."""

    # Find all the segments that are "moving", defined as having a speed above
    # 1 meter per second. Instead of using the raw speeds, check against the
    # filtered speeds. Additionally, a segment can only count as "moving" if it
    # is part of a series of at least 3 segments that satisfy all other
    # criteria for "moving".
    moving_segs = []
    motionless_segs = []
    tmp_moving_segs = []
    for idx, speed in enumerate(filt_speeds):
        if speed >= 1.0 and speed <= 1000:
            tmp_moving_segs.append(segments[idx])
        elif len(tmp_moving_segs) < 3:
            motionless_segs.append(tmp_moving_segs)
            del tmp_moving_segs
            tmp_moving_segs = []
        elif len(tmp_moving_segs) > 2:
            moving_segs.append(tmp_moving_segs)
            del tmp_moving_segs
            tmp_moving_segs = []
    print("Found all '{}' segments which represent movement, and all '{}' segments which are motionless".format(len(moving_segs), len(motionless_segs)))

    return moving_segs, motionless_segs




def main():
    start_time = "09:00:00 01-04-15"
    stop_time = "19:00:00 23-04-15"

    start_time = time_utils.simplefmt_in_pdt_to_utc_epoch(start_time)
    stop_time = time_utils.simplefmt_in_pdt_to_utc_epoch(stop_time)
    print('begin_UTC_Epoch:', start_time)
    print('end_UTC_Epoch:', stop_time)

    # Gather entries from database, transform into segments
    entries = whereis.AutoDB().get_date_range(start_time, stop_time)
    segments = []
    for idx in range(1, len(entries)):
        tmp_seg = geo_utils.Segment(entries[idx-1], entries[idx])
        segments.append(tmp_seg)
    # Make sure that the correct number of segments have been created for the
    # amount of entries
    assert len(segments) == (len(entries) - 1)
    print("Created '{}' segments from entries".format(len(segments)))

    speeds = [s.speed for s in segments]
    filt_speeds = geo_utils.median_filter(speeds, winlen=5)
    # Ensure that we have a correct number of filtered speed values
    assert len(filt_speeds) == len(segments)

    # Get moving and motionless segments
    moving_segs, motionless_segs = designate_moving_segments(segments, filt_speeds)

    coords = [[float(ent['latitude']), float(ent['longitude'])] for ent in entries]

    mov_coords = [[float(seg.last['latitude']), float(seg.last['longitude'])] for seg in chain.from_iterable(moving_segs)]

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


