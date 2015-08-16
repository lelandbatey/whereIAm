from __future__ import print_function
from models import entry_model
import datetime
import json
#pylint: disable=W0312

def json_dump(indata):
	"""Creates prettified json representation of passed in object."""
	return json.dumps(indata, sort_keys=True, indent=4, \
		separators=(',', ': '))#, cls=date_handler)
def jp(indata):
	"""Prints json representation of object"""
	print(json_dump(indata))


def log_to_dict(filename='gpsRecord.log'):
	"""Converts a dictlog file into a list of dictionaries."""
	raw_lines = []
	with open(filename, 'r') as log_file:
		raw_lines = log_file.read().splitlines()
	to_return = []
	# to_return = [
	# 	{key: value for pair in line.split(',') for key, value in [pair.split('=')] } for line in raw_lines
	# ]
	for index, line in enumerate(raw_lines):
		if not line: continue
		tmp_dict = {}
		for pair in line.split(','):
			try:
				key, value = pair.split('=')
			except Exception as e:
				print("Line #:", index)
				print(line)
				print(pair.split('='))
				raise e
			tmp_dict[key] = value
		to_return.append(tmp_dict)
	return to_return



def main():
	old_log = log_to_dict()

	model = entry_model.LocationModel()
	for index, value in enumerate(old_log):
		if not index % 1000:
			print("{:<8} entries".format(index))
			model.new_entry(value)
		else:
			model.new_entry(value, False)
	model.session.commit()
	print("Finished.")
	# jp(log_to_dict())



if __name__ == '__main__':
	main()
