import datetime
import dateutil.parser
import pytz

def parseSessionDuraction(val):
	total = 0

	valSplit = val.split(" ")
	timeSplit = None
	if len(valSplit) > 1:
		timeSplit = valSplit[1]
		dayCount = valSplit[0].split("d")[0]
		if dayCount.isdigit():
			total += int(dayCount) * 24 * 60 * 60
	
	else:
		timeSplit = valSplit[0]

	ts = timeSplit.split(":")
	hourCount = ts[0].split("h")[0]
	if hourCount.isdigit():
		total += int(hourCount) * 60 * 60

	minuteCount = ts[1].split("m")[0]
	if minuteCount.isdigit():
		total += int(minuteCount) * 60

	secondCount = ts[2].split("s")[0]
	if secondCount.isdigit():
		total += int(secondCount)

	return total

PARSER_CONF = {
	"general": {
		# in seconds
		"time_interval": 60 * 30, # 30 minutes either way
	},

	# How to structure this configuration...
	"bro": {
		# All of the files that we should transfer from the original files (and should keep the same key as the original data)
		# If 'transfer_fields' is False or empty then we only use 'ignore_fields'
		"transfer_fields": False,
		# 'ignore_fields' is only used if 'transfer_fields' is False or empty.
		# If using 'ignore_fields' we tranfer all of the fields from the original data except for the keys in this list
		"ignore_fields": ["proto", "origin_ip", "source_port", "dest_ip", "dest_port", "timestamp", "ts", "sourceType", "sourcetype"],
		# Transfer/Ignore fields is the first action taken, so fields might be overwriten with fields specified in 'parse_fields'
		# The named fields that need to be the same for every file
		"parse_fields": {
			# The direct (or multiple) translations
			"fields": {
				# The overall 'src_ip' should get gotten from bro's 'source_ip'
				"src_ip": "origin_ip",
				"src_port": "source_port",
				"dst_ip": "dest_ip",
				"dst_port": "dest_port",
				# If it's an array, then on the original data files there might be multiple keys for timestamp
				# In this case we go one by one and grab just the first value we can find
				"timestamp": ["timestamp", "ts"],
				"protocol": "proto",
			},
			# If we need to parse some of the data the same field should appear here
			"parse": {
				"timestamp": (lambda x: datetime.datetime.utcfromtimestamp(float(x)).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()),
			},
		},

		# Extra scripted fields to add
		# Each key will be the name of the field to add to the line
		# and should correspond to a function, which will be called with the current fields already parsed
		# These are the last functions to be called, so all the props before are already in the object these are called with
		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),
		},
	},

	"pan": {
		"transfer_fields": False,
		"ignore_fields": ["proto", "src", "srcPort", "dst", "dstPort", "datetime", "totalBytes", "DeviceName", "sourceType", "ElapsedTime"],
		"parse_fields": {
			"fields": {
				"src_ip": "src",
				"src_port": "srcPort",
				"dst_ip": "dst",
				"dst_port": "dstPort",
				"timestamp": "datetime",
				"protocol": "proto",
				"des_total_bytes": "totalBytes",
				"des_src_bytes": "srcBytes",
				"des_dst_bytes": "dstBytes",
				"des_session_duration": "ElapsedTime",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),
			
			# Hack because pan can have "DeviceName" and it's more descriptive for the most part
			"des_device_name": (lambda x: x["DeviceName"] if "DeviceName" in x else x["des_device_name"]),
		},
	},

	"ciscoasa": {
		"transfer_fields": False,
		"ignore_fields": ["protocol", "src_ip", "src_port", "dst_ip", "dst_port", "@timestamp", "type"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": "src_port",
				"dst_ip": "dst_ip",
				"dst_port": "dst_port",
				"timestamp": "@timestamp",
				"protocol": "protocol",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: [y.lower() for y in x] if type(x) is list else x.lower()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),
		},
	},

	"ciscovpn": {
		"transfer_fields": False,
		"ignore_fields": ["ip", "@timestamp", "type"],
		"parse_fields": {
			"fields": {
				"src_ip": "ip",
				"src_port": False,
				"dst_ip": False,
				"dst_port": False,
				"timestamp": "@timestamp",
				"protocol": False,
				"des_src_bytes": "bytes_received",
				"des_dst_bytes": "bytes_transmitted",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),

			"des_total_bytes": (lambda x: (int(x["bytes_received"]) + int(x["bytes_transmitted"])) if "bytes_received" in x and x["bytes_received"].isdigit() and "bytes_transmitted" in x and x["bytes_transmitted"].isdigit() else None),
			"des_session_duration": (lambda x: parseSessionDuraction(x["session_duration"]) if "session_duration" in x else None),
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
				"protocol": False,
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),
		},
	},

	"suricata": {
		"transfer_fields": False,
		"ignore_fields": ["proto", "src_ip", "src_port", "dest_ip", "dest_port", "timestamp", "date"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": "src_port",
				"dst_ip": "dest_ip",
				"dst_port": "dest_port",
				"timestamp": ["timestamp", "date"],
				"protocol": "proto",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()), 
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x: "%s -> %s" % (x["src_ip"], x["dst_ip"])),
			"port_pair": (lambda x: "%s -> %s" % (x["src_port"], x["dst_port"])),
			"ip_port_pair": (lambda x: "%s:%s -> %s:%s" % (x["src_ip"], x["src_port"], x["dst_ip"], x["dst_port"])),
		},
	}
}