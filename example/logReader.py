from __future__ import print_function
import json

# 
# Log Reader Example Code
# -----------------------

# Since the log format is so odd, I've included this code as a way to read the
# log file format back into dictionary. It does not serialize the data into
# their correct types, it leaves everything as strings. You'll have to do that
# part yourself.


_LOG_FILE_NAME_ = 'exampleLog.log'



def jdump(inputData):
	return json.dumps(inputData, sort_keys=True, indent=3, separators=(',', ': '))

def logToDict(logLine):
	# Sorry for all the list/dict comprehensions, they're just so handy!
	logLine = logLine.strip().split(',')
	logLine = [x for x in logLine if x] # removes any empty entries in the list
	logLine = [x.split('=') for x in logLine]
	returnDict = {x[0]: x[1] for x in logLine }
	# Above dict comprehension is equivalent of the following:
	# for x in logLine:
	# 	returnDict[x[0]] = x[1]
	return returnDict




oldFile = open(_LOG_FILE_NAME_,'r')

for line in oldFile:
	print(jdump(logToDict(line)))

