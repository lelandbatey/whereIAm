
import math
# Below taken from here:
#     http://www.johndcook.com/blog/python_longitude_latitude/
def distance_on_unit_sphere(lat1, long1, lat2, long2):
	"""Calculates the distance between two lat/long points. Returns distance in
	'arc length' format that's relative to the radius of earth. To get the
	distance in miles, multiply the result by 3960, while to get the distance
	in kilometers multiply the result by 6373."""
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
	time = entry1.monotonic_timestamp - entry0.monotonic_timestamp
	return distance / time

def speed_for_series(entries):
	"""Function prints information on a series of 'LocationEntry' objects."""
	for i in range(0, len(entries)-2):
		speed_meters_ps = get_speed(entries[i], entries[i+1])
		# print("Speed in m/s:", speed_meters_ps)
		kilometers_ph = (speed_meters_ps * 3600.0) / 1000
		# print("Speed in k/h:", kilometers_ph)
		entries[i+1].data['speed'] = kilometers_ph

	speed_sum = sum([x.data['speed'] for x in entries])
	avg_speed = speed_sum/float(len(entries))
	#print("The sum of speeds is", speed_sum)
	#print("Number of entries:", len(entries))
	#print("The average speed for this range of data is: {} kilometers per hour.".format(avg_speed))
	return entries
