# -*- coding: utf-8 -*-

"""Segment is a class which represents information about a line-segment between
two GPS coordinates."""

from . import calculate_bearing, distance_on_unit_sphere, get_speed


class Segment(object):
    """Represents data about the line-segment between two GPS coordinates."""
    def __init__(self, first_entry, last_entry):
        """Initialize the coordinates which define this Segment, as well as
        this Segments `bearing` (in radians from North), `linear_length` (in
        meters), and `speed` (in meters per second)."""
        self.first = first_entry
        self.last = last_entry

        self.bearing = calculate_bearing(self.first, self.last)

        arc_distance = distance_on_unit_sphere(
                self.first['latitude'], self.first['longitude'],
                self.last['latitude'], self.last['latitude']
                )
        # Multiply the arc-length by the radius of the earth in meters to get
        # the length in meters
        self.linear_length = arc_distance * 6378100

        self.speed = get_speed(self.first, self.last)

        ts0 = self.first['monotonic_timestamp']
        ts1 = self.last['monotonic_timestamp']
        self.mean_timestamp = (ts0 + ts1) / 2.0

