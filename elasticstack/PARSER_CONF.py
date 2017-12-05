import datetime
import dateutil.parser
import pytz

PARSER_CONF = {
	"general": {
		# in seconds
		"time_interval": 60 * 10,
	},

	# How to structure this configuration...
	"bro": {
		# All of the files that we should transfer from the original files (and should keep the same key as the original data)
		# If 'transfer_fields' is False or empty then we only use 'ignore_fields'
		"transfer_fields": False,
		# 'ignore_fields' is only used if 'transfer_fields' is False or empty.
		# If using 'ignore_fields' we tranfer all of the fields from the original data except for the keys in this list
		"ignore_fields": ["origin_ip", "source_port", "dest_ip", "dest_port", "timestamp", "ts"],
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
				"protocol": "proto",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()),
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
				"protocol": "protocol",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: [y.lower() for y in x] if type(x) is list else x.lower()),
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
				"protocol": False,
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
				"protocol": False,
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
				"protocol": "proto",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()), 
			},
		},
	}
}