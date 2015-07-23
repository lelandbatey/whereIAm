from __future__ import print_function
from pprint import pprint
import math as M

# Given the hypothetical data, find the angles (in radians) between points

#pylint: disable=C0330
#pylint: disable=W0312
#pylint: disable=W0141

def rad_to_deg(r):
	return r * (180.0/M.pi)

def calculate_bearing(raw_data):
	in_place_data = [x.copy() for x in raw_data]
	for i in range(1, len(raw_data)):
		first, second = raw_data[i-1], raw_data[i]
		lat1, lon1 = float(first['latitude']), float(first['longitude'])
		lat2, lon2 = float(second['latitude']), float(second['longitude'])
		dLon = lon2 - lon1
		y = M.sin(dLon) * M.cos(lat2)
		x = M.cos(lat1) * M.sin(lat2) - M.sin(lat1)*M.cos(lat2)*M.cos(dLon)
		bearing = M.atan2(y, x)
		# print(bearing)
		in_place_data[i]['derived_bearing'] = bearing
	return in_place_data




def calculate_angles(raw_data):
	in_place_data = raw_data.copy()
	new_data = []
	for i in range(1, len(raw_data)):
		first, second = raw_data[i-1], raw_data[i]
		def getxynums(dat): return map(float, [dat['x'], dat['y']])
		fnums, snums = map(getxynums, [first, second])
		def re_origin_xy(alpha, beta):
			alpha, beta = list(alpha), list(beta)
			return [beta[0]-alpha[0], beta[1]-alpha[1]]
		# print(list(fnums), list(snums))
		# print(re_origin_xy(fnums, snums)
		angle = M.atan2(*reversed(re_origin_xy(fnums, snums)))
		print('{}-{}'.format(i-1, i), rad_to_deg(angle))
		new_data.append(angle)
		in_place_data[i-1]['angle'] = angle
	return in_place_data, new_data



#pylint: disable=C0330
def test_calculate_bearing():
	"""Tests to ensure that the bearing calculated between two points is
	correct."""

	point_pairs = [
		[
			{ # From end of Davison Ave to in front of my house.
				"latitude": 46.323865,
				"longitude": -119.267288
			},
			{
				"latitude": 46.323006,
				"longitude": -119.267427
			}
		]
	]
	for pair in point_pairs:
		pprint(calculate_bearing(pair))

if __name__ == '__main__':
	test_calculate_bearing()