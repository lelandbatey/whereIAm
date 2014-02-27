from __future__ import print_function
from flask import Flask, request
from pprint import pprint
import flask
import json


log_file_name = "gpsRecord.log"

app = Flask(__name__)

gpsData = [{
   "accuracy": "38.618",
   "altitude": "0.0",
   "bearing": "0.0",
   "latitude": "46.3228938",
   "longitude": "-119.2677629",
   "provider": "network",
   "speed": "0.0",
   "time": "2014-02-20T04:55:49.603Z"
}] # This will always be at least the first item in the list. Makes it simple to start

def oneLine(inputObject):
	finalStr = ""

	temp = [ str(x)+"="+str(inputObject[x]) for x in inputObject.keys()]
	# The above list comprehension is the equivelent of the following
	# for x in inputObject.keys():
	# 	temp.append(str(x)+"="+str(inputObject[x]))
	
	finalStr = ','.join(temp)
	return (finalStr+'\n')


def logStr(inputObj):
	recordFile = open(log_file_name,'a')
	recordFile.write(oneLine(inputObj))
	recordFile.close()
	return

def jsonContent(inputData):
	response = flask.make_response(inputData)
	response.headers["Content-type"] = "application/json"
	return response

def jdump(inputData):
	return json.dumps(inputData, sort_keys=True, indent=3, separators=(',', ': '))

@app.route('/update', methods=['POST','GET'])
def update():
	# pprint(request.form)
	# print(jdump(request.form))
	gpsData.append(request.form)
	logStr(request.form)
	return ""

@app.route('/currentpos')
def currentPos():
	data = jdump(gpsData[-1])
	return jsonContent(data)

@app.route('/allpos')
def allPos():
	allData = jdump(gpsData)
	return jsonContent(allData)

@app.route('/')
def mainPage():
	return flask.render_template("mainpage.html")


if __name__ == '__main__':
	app.run(port=8001)








