from __future__ import print_function
import unittest
import math

import filter_moving


class SimpleSegmentTests(unittest.TestCase):
    """Ensure that SimpleSegment correctly calculates it's data."""

    def setUp(self):
        """Generate some lat/lon coordinates."""
        self.first = {
            "latitude": 46.0,
            "longitude": -120.0,
            "monotonic_timestamp": 0
        }
        self.second = {
            "latitude": 45.995,
            "longitude": -120.0,
            "monotonic_timestamp": 1
        }
        self.south = self.second
        self.north = self.first
        self.east = {
            "latitude": 46.0,
            "longitude": -120.000,
            "monotonic_timestamp": 2
        }
        self.west = {
            "latitude": 46.0,
            "longitude": -121.0000,
            "monotonic_timestamp": 3
        }

    def test_begin_end(self):
        seg = filter_moving.SimpleSegment(self.first, self.second)
        self.assertEqual(seg.begin, self.first)
        self.assertEqual(seg.end, self.second)

    def test_derived_bearing(self):
        seg = filter_moving.SimpleSegment(self.north, self.south)
        self.assertEqual(round(seg.derived_bearing, 2), 3.14)
        seg = filter_moving.SimpleSegment(self.east, self.west)
        self.assertEqual(round(seg.derived_bearing, 2), -1.56)

    def test_speed(self):
        seg = filter_moving.SimpleSegment(self.first, self.second)
        self.assertEqual(math.floor(seg.speed), 556)
        # print(seg.speed)
