#!/usr/env python
from __future__ import print_function

import os.path
import json
import os

def jdump(j): return json.dumps(j, separators=(',',':'), indent=4, sort_keys=True)

def training_data_files(fpath):
	fpath = os.path.abspath(fpath)
	rv = []
	for train_file in os.listdir(fpath):
		rv.append(os.path.join(fpath, train_file))
	return rv

def training_data_raw(paths):
	rv = {}
	for p in paths:
		with open(p, 'r') as jfile:
			rv[p] = json.load(jfile)
	return rv


def training_data_distill(raw):
	rv = []
	for name in raw.keys():
		full_data=None
		if "BAD" not in name:
			full_data = raw[name]
		if full_data:
			for entry in full_data:
				pure = {}
				inpt = entry['train_data']
				outpt = entry['is_moving_human_evaluation']
				pure['input'] = inpt
				if not outpt:
					pure['output'] = {'motionless': 1}
				else:
					pure['output'] = {'moving': 1}
				rv.append(pure)
	return rv



def main():
	tpaths = training_data_files('../training_data_clean/')
	traw = training_data_raw(tpaths)
	distilled = training_data_distill(traw)
	print(jdump(distilled))
	#print(training_data_files('../training_data/'))



if __name__ == '__main__':
	main()

