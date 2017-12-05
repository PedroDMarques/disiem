import sys
import os
import traceback

import datetime
import dateutil.parser
import pytz

import json

ELASTICSEARCH_INDEX = "disiem"

DATA_FOLDER = "data"
SAVE_FOLDER = "data_elasticstack"

# A list of software names to filter from the convertion
IGNORE_SOFTWARE = ["bro", "pan", "ciscoasa", "ciscovpn"]
# A list of device names to filter from the convertion
IGNORE_DEVICE = []

PARSER_CONF = {
	# How to structure this configuration...
	"bro": {
		# All of the files that we should transfer from the original files (and should keep the same key as the original data)
		# If 'transfer_fields' is False or empty then we only use 'ignore_fields'
		"transfer_fields": False,
		# 'ignore_fields' is only used if 'transfer_fields' is False or empty.
		# If using 'ignore_fields' we tranfer all of the fields from the original data except for the keys in this list
		"ignore_fields": ["source_ip", "source_port", "dest_ip", "dest_port", "timestamp", "ts"],
		# Transfer/Ignore fields is the first action taken, so fields might be overwriten with fields specified in 'parse_fields'
		# The named fields that need to be the same for every file
		"parse_fields": {
			# The direct (or multiple) translations
			"fields": {
				# The overall 'src_ip' should get gotten from bro's 'source_ip'
				"src_ip": "source_ip",
				"src_port": "source_port",
				"dst_ip": "dest_ip",
				"dst_port": "dest_port",
				# If it's an array, then on the original data files there might be multiple keys for timestamp
				# In this case we go one by one and grab just the first value we can find
				"timestamp": ["timestamp", "ts"],
			},
			# If we need to parse some of the data the same field should appear here
			"parse": {
				"timestamp": (lambda x: datetime.datetime.utcfromtimestamp(float(x)).replace(tzinfo=pytz.utc).isoformat()),
			},
		},
	},

	"pan": {
		"transfer_fields": False,
		"ignore_fields": ["src", "srcPort", "dst", "dstPort", "datetime"],
		"parse_fields": {
			"fields": {
				"src_ip": "src",
				"src_port": "srcPort",
				"dst_ip": "dst",
				"dst_port": "dstPort",
				"timestamp": "datetime",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},
	},

	"ciscoasa": {
		"transfer_fields": False,
		"ignore_fields": ["src_ip", "src_port", "dst_ip", "dst_port", "@timestamp"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": "src_port",
				"dst_ip": "dst_ip",
				"dst_port": "dst_port",
				"timestamp": "@timestamp",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},
	},

	"ciscovpn": {
		"transfer_fields": False,
		"ignore_fields": ["ip", "@timestamp"],
		"parse_fields": {
			"fields": {
				"src_ip": "ip",
				"src_port": False,
				"dst_ip": False,
				"dst_port": False,
				"timestamp": "@timestamp",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},
	},

	"mcafee": {
		"transfer_fields": False,
		"ignore_fields": ["src_ip", "dest_ip", "datetime"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": False,
				"dst_ip": "dest_ip",
				"dst_port": False,
				"timestamp": "datetime",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},
	},

	"suricata": {
		"transfer_fields": False,
		"ignore_fields": ["src_ip", "src_port", "dest_ip", "dest_port", "timestamp"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": "src_port",
				"dst_ip": "dest_ip",
				"dst_port": "dest_port",
				"timestamp": "timestamp",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()), 
			},
		},
	}
}

_indexCounter = 0

def parseEventLine(line, conf, additionalFields):
	"""
	Parses a single line of an event and returns a new line to write to disk
	This new line includes the headers necessary for elasticstack
	@param {string} line The line to parse
	@param {dict} conf The configuration object
	@param {dict} additionalFields Additional fields to add to the returning object
	"""
	parsed = dict()
	props = json.loads(line)

	# If transfer_fields is in use use that to transfer specific fields
	if conf["transfer_fields"]:
		for field in conf["transfer_fields"]:
			if field in props:
				parsed[field] = props[field]

	# Otherwise transfer all fields and just ignore some
	else:
		for field in props:
			if field not in conf["ignore_fields"]:
				parsed[field] = props[field]

	for field in conf["parse_fields"]["fields"]:
		value = None
		propsKey = conf["parse_fields"]["fields"][field]
		# There is no translation in the target software so just break out
		if not propsKey:
			parsed[field] = value
			continue
			
		# There might be multiple keys in the target
		if type(propsKey) is list:
			for subKey in propsKey:
				if subKey in props:
					value = props[subKey]
					break
		
		# There is just one key in the target
		else:
			if propsKey in props:
				value = props[propsKey]

		# We need to parse the value before sending it
		if field in conf["parse_fields"]["parse"]:
			value = conf["parse_fields"]["parse"][field](value)

		parsed[field] = value

	for field in additionalFields:
		parsed[field] = additionalFields[field]

	global _indexCounter
	_indexCounter += 1
	return ('{"index":{"_index":"%s","_type":"%s","_id":"%d"}}\n%s\n' %
					(ELASTICSEARCH_INDEX, ELASTICSEARCH_INDEX, _indexCounter, json.dumps(parsed)))

class ConvertionFile(object):
	def __init__(self, path):
		self.path = path
		self.dirPath = os.path.dirname(path)
		self.software = path.split("\\")[0]
		self.device = path.split("\\")[1]

	def getPath(self):
		return self.path

	def getDirPath(self):
		return self.dirPath

	def getSoftware(self):
		return self.software

	def getDevice(self):
		return self.device

	def __repr__(self):
		return str(self.path)

	def __str__(self):
		return str(self.path)

def getConvertionFiles(basePath, cyclePath=""):
	nextPath = os.path.join(basePath, cyclePath)

	convertionFiles = []
	for fname in os.listdir(nextPath):
		newCyclePath = os.path.join(cyclePath, fname)
		fullPath = os.path.join(basePath, newCyclePath)
		
		if os.path.isdir(fullPath):
			convertionFiles += getConvertionFiles(basePath, newCyclePath)
		else:
			convertionFiles.append(ConvertionFile(newCyclePath))

	return convertionFiles

def convertFile(convertionFile, baseDataPath, baseSavePath):
	# Create destination folders if they don't exist
	if not os.path.exists(os.path.join(baseSavePath, convertionFile.getDirPath())):
		os.makedirs(os.path.join(baseSavePath, convertionFile.getDirPath()))

	inFilePath = os.path.join(baseDataPath, convertionFile.getPath())
	outFilePath = os.path.join(baseSavePath, convertionFile.getPath())

	with open(inFilePath, "r") as inFile, open(outFilePath, "w") as outFile:
		for line in inFile:
			try:
				# Hack for mcaffee
				if convertionFile.getSoftware() == "mcafee":
					line = r"%s" % line

				additionalFields = {
					"disiem_software_type": convertionFile.getSoftware(),
					"disiem_device_name": convertionFile.getDevice()
				}
				outFile.write(parseEventLine(line, PARSER_CONF[convertionFile.getSoftware()], additionalFields))

			except ValueError as e:
				raise e
				print "\tERROR: Can't decode line %d\n\t%s" % (_indexCounter, line)
				traceback.print_exc()
			except Exception as e:
				print e

def main(dataPath, savePath):
	convertionFiles = getConvertionFiles(dataPath)

	if IGNORE_SOFTWARE:
		nFiles = len(convertionFiles)
		convertionFiles = [x for x in convertionFiles if x.getSoftware() not in IGNORE_SOFTWARE]
		print "Filtered %d files based on software" % (nFiles - len(convertionFiles))
		print "------------------------------------------"

	if IGNORE_DEVICE:
		nFiles = len(convertionFiles)
		convertionFiles = [x for x in convertionFiles if x.getDevice() not in IGNORE_DEVICE]
		print "Filtered %d files based on device" % (nFiles - len(convertionFiles))
		print "------------------------------------------"

	for f in convertionFiles:
		print "Converting [%s]" % f
		convertFile(f, dataPath, savePath)
	
	print "------------------------------------------"
	print "Finished"
	print "Converted %d files to elasticsearch syntax" % len(convertionFiles)

if __name__ == "__main__":
	main(
		os.path.join(os.getcwd(), DATA_FOLDER),
		os.path.join(os.getcwd(), SAVE_FOLDER)
	)