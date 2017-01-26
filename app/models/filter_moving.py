'''
Module filter_moving exposes functions for the filtering of raw coordinates
over time into moving and non-moving coordinates, and the de-duplication of
those non-moving coordinates.
'''

import geo_utils


class SimpleSegment(object):
    """Class SimpleSegment contains data about a pair of coordinates."""
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        self.derived_bearing = geo_utils.calculate_bearing(begin, end)
        # Multiplies distance as arc-length by the radius of the earth in
        # meters to get the length in meters
        self.linear_length = geo_utils.distance_on_unit_sphere(
            self.begin['latitude'], self.begin['longitude'],
            self.end['latitude'], self.end['longitude']) * 6378100
        ts = 'monotonic_timestamp'
        self.duration = self.end[ts] - self.begin[ts]
        self.speed = geo_utils.get_speed(self.begin, self.end)


def designate_movement(series):
    f
