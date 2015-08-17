"""

Wraps a simple list-based representation of an xy coordinate in an object to
properly handle coordinate addition, subtraction, multiplication. Lets
coordinates be passed to a KalmanFilter without breaking the KalmanFilter.

"""

from __future__ import print_function
from numbers import Real

class Coordinate(object):
    def __init__(self, c):
        self.x = c[0]
        self.y = c[1]
    
    def __add__(self, obj):
        if isinstance(obj, Coordinate):
            return Coordinate([obj.x+self.x, obj.y+self.y])
        elif isinstance(obj, Real):
            return Coordinate([self.x + obj, self.y + obj])
        else:
            raise TypeError("Cannot add non-number type to a coordinate")

    def __sub__(self, obj):
        if isinstance(obj, Coordinate):
            return Coordinate([self.x - obj.x, self.y - obj.y])
        elif isinstance(obj, Real):
            return Coordinate([self.x - obj, self.y - obj])
        else:
            raise TypeError("Cannot subtract non-number type from a coordinate")

    def __mul__(self, obj):
        if isinstance(obj, Real):
            return Coordinate([self.x*obj, self.y*obj])
        else:
            raise TypeError("Coordinates can only be multiplied by real numbers")


