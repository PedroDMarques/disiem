import argparse

def parseArgs():
	parser = argparse.ArgumentParser(
		description="Parse amadeus data files, and either write them to disk parsed, or send them directly to elasticsearch"
	)
	
	parser.add_argument("-v", "--verbose", action="count",
		help="With -v each file filtered will be shown. With -vv both files filtered and passed will be shown")
	
	parser.add_argument("mode", 
		choices=["plot","parse", "send", "send-parsed", "parse-send", "send-parse", "rank-parsed", "list", "impossible-timestamps", "noop", "config-write", "config-list", "reset-elasticsearch", "output", "create-index", "delete-index", "collect-parsed", "collect-parsed-ex"]
	)

	parser.add_argument("-c", "--config", default="config.cfg", dest="config_location",
		help="Relative path to the configuration file. If used in 'config-write' mode, dictates the file to write to. Defaults to 'config.cfg'"
	)
	
	parser.add_argument("--default-config", action="store_true",
		help="If set will use a default config object instead of reading one from a file. If used in 'config-write' mode writes a config file with default values"
	)

	parser.add_argument("--specific-files",
		help="Specify the location of a the data files to work on. This path should be relative to the 'data_location' config value and different files separated by commas"
	)

	parser.add_argument("-n", "--number-lines", type=int,
		help="When using in 'output' mode specifies the number of lines per file that should be outputed"
	)

	parser.add_argument("--include-files",
		help="Specify the location of data files to force include in the parsing, even if they are to be filtered out. Should be a list of strings separated by commas"
	)

	parser.add_argument("--es-index",
		help="Specify the elasticsearch index to use for the operation"
	)

	parser.add_argument("-p", "--plot",
		choices=["software-alerts", "suricata-alerts", "ciscoasa-alerts", "pan-alerts", "device-alerts", 
			"suricata-protocol", "ciscoasa-protocol", "pan-protocol"]
	)

	parser.add_argument("--testing", action="store_true",
		help="Used for debuging"
	)

	return parser.parse_args()