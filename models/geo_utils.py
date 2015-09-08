from __future__ import print_function
import math

#pylint: disable=W0312


# Below taken from here:
#     http://www.johndcook.com/blog/python_longitude_latitude/
def distance_on_unit_sphere(lat1, long1, lat2, long2):
	"""Calculates the distance between two lat/long points. Returns distance in
	'arc length' format that's relative to the radius of earth. To get the
	distance in miles, multiply the result by 3960, while to get the distance
	in kilometers multiply the result by 6373."""

	lat1, long1 = float(lat1), float(long1)
	lat2, long2 = float(lat2), float(long2)
	# Convert latitude and longitude to
	# spherical coordinates in radians.
	degrees_to_radians = math.pi/180.0

	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians

	# theta = longitude
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians

	# Compute spherical distance from spherical coordinates.

	# For two locations in spherical coordinates
	# (1, theta, phi) and (1, theta, phi)
	# cosine( arc length ) =
	#    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
	# distance = rho * arc length

	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
	cos = min(1, max(cos, -1))
	try:
		arc = math.acos(cos)
	except Exception, e:
		#print("Cos:", cos)
		#print(e)
		raise e

	# Remember to multiply arc by the radius of the earth
	# in your favorite set of units to get length.
	return arc


def get_speed(entry0, entry1):
	"""Given two 'LocationEntry' objects, returns speed traveled between the
	two them. Return value is in form of meters per second."""

	arc_distance = distance_on_unit_sphere(entry0.latitude, entry0.longitude, entry1.latitude, entry1.longitude)
	# Multiplying the arc distance by the radius of the earth in meters. Gets
	# us the distance in meters.
	distance = arc_distance * 6378100
	distance = round(distance, 4)
	time = entry1.monotonic_timestamp - entry0.monotonic_timestamp
	if distance == 0.0:
		return 0.0
	speed = distance / time
	if speed < 0.0:
		print('distance:', distance)
		print('speed:', speed)
		print('time:', time)
		print('ts0:', entry0.monotonic_timestamp)
		print('ts1:', entry1.monotonic_timestamp)
	return distance / time

def speed_for_series(entries):
	"""Function prints information on a series of 'LocationEntry' objects."""
	raise NotImplementedError
	for i in range(0, len(entries)-2):
		speed_meters_ps = get_speed(entries[i], entries[i+1])
		kilometers_ph = (speed_meters_ps * 3600.0) / 1000
		# Should not modify the in-place data...
		entries[i+1].data['speed'] = kilometers_ph

	speed_sum = sum([x.data['speed'] for x in entries])
	try:
		avg_speed = speed_sum/float(len(entries))
	except Exception as e:
		print("speed_sum:", speed_sum)
		print('entries:', entries)
		print('float(len(entries)):', float(len(entries)))
		raise e
	return entries

def calculate_bearing(raw_data):
	in_place_data = [x.copy() for x in raw_data]
	for i in range(1, len(raw_data)):
		first, second = raw_data[i-1], raw_data[i]
		lat1, lon1 = float(first['latitude']), float(first['longitude'])
		lat2, lon2 = float(second['latitude']), float(second['longitude'])
		dLon = lon2 - lon1
		y = math.sin(dLon) * math.cos(lat2)
		x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
		bearing = math.atan2(y, x)
		# print(bearing)
		in_place_data[i]['derived_bearing'] = bearing
	return in_place_data


def get_candidates(data, index, winlen):
	assert (winlen % 2) == 1
	middle = winlen // 2

	too_short = False
	too_long = False
	start = index-middle
	if start < 0:
		start = 0
		too_short = True
	end = index+middle
	if end > len(data)-1:
		end = len(data)-1
		too_long = True

	calc_desired = end - start+1
	candidates = []
	while len(candidates) < calc_desired:
		candidates.append(data[start])
		start += 1

	while len(candidates) < winlen:
		if too_short:
			candidates.insert(0, candidates[0])
		if too_long and len(candidates) < winlen:
			candidates.append(candidates[-1])

	assert len(candidates) == winlen
	return candidates


def median_filter(data, winlen=3):
	medians = []
	middle = winlen // 2

	for item in range(0, len(data)):
		candidates = sorted(get_candidates(data, item, winlen))
		medians.append(candidates[middle])
	return medians


def format_xy_matplotlib(rawxy):
	y, x = zip(*rawxy)
	x = [-n for n in x]
	return x, y

def mean(data, accessor=lambda x: x):
	data = [accessor(item) for item in data]
	m = float(sum(data))/len(data) if len(data) > 0 else float('nan')
	return m
