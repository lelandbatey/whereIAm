# -*- coding: utf-8 -*-

"""Tests for the geo_utils.py file. Since `geo_utils` is both a file name and a
module name, I'm deciding that in the future, no more code shall be added to
`geo_utils.py`. Instead, specific functionality will go in seperate files, and
each file will have a sibling file named `test_{file_name.py}` that contains
that code's tests."""

from __future__ import print_function
import unittest
import numbers
import math

# import whereIAm.models.geo_utils.geo_utils as geo_utils
from .. import geo_utils



class TestCalculateBearing(unittest.TestCase):
    """Unit tests for the `calculate_bearing` function."""
    def setUp(self):
        """Generate some lat/lon coordinates."""
        import mpmath as mp
        self.first = {"latitude" : 46.0,
                      "longitude": -120.0}
        self.second = {"latitude" : 45.995,
                       "longitude": -120.0}

        # self.east = {"latitude" : mp.mpf(46.0),
                     # "longitude": mp.mpf(-120.0)}
        # self.west = {"latitude" : mp.mpf(46.0),
                     # "longitude": mp.mpf(-120.0001)}
        self.east = {"latitude" : 46.0,
                     "longitude": -120.0}
        self.west = {"latitude" : 46.0,
                     "longitude": -121.0}

    def test_input_attributes(self):
        """Check that odd objects with only `latitude` and `longitude`
        dictionary attributes will still be validly interpreted."""
        self.first['NoN-Needed_attr'] = float('nan')
        self.second['bad_valuuuus '] = float('nan')

        result = geo_utils.calculate_bearing(self.first, self.second)
        self.assertTrue(isinstance(result, numbers.Real))

    def test_vertical_up_bearing(self):
        """Test that a first point exactly below the second point yields a
        bearing of `0.0`."""
        start = self.second
        end = self.first

        result = geo_utils.calculate_bearing(start, end)
        self.assertEqual(result, 0.0)

    def test_vertical_down_bearing(self):
        """Test that a first point exactly above a second point yields a
        bearing of PI."""
        start = self.first
        end = self.second

        result = geo_utils.calculate_bearing(start, end)
        self.assertEqual(result, math.pi)

    def test_east_west_horizontal_bearing(self):
        """Test that a starting point exactly east of the ending point yields a
        bearing of (-PI)/2.0"""
        start = self.east
        end = self.west

        result = geo_utils.calculate_bearing(self.east, self.west)
        print(math.degrees(result))
        self.assertEqual(result, (-math.pi)/2.0)






