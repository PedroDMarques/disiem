import argparse

def parseArgs():
	parser = argparse.ArgumentParser(
		description="Parse amadeus data files, and either write them to disk parsed, or send them directly to elasticsearch"
	)
	
	parser.add_argument("-v", "--verbose", action="count",
		help="With -v each file filtered will be shown. With -vv both files filtered and passed will be shown")
	
	parser.add_argument("mode", 
		choices=["write", "send", "list", "impossible-timestamps", "noop", "config-write", "config-list", "reset-elasticsearch"]
	)

	parser.add_argument("-c", "--config", default="config.cfg", dest="config_location",
		help="Relative path to the configuration file. If used in 'config-write' mode, dictates the file to write to. Defaults to 'config.cfg'"
	)
	
	parser.add_argument("--default-config", action="store_true",
		help="If set will use a default config object instead of reading one from a file. If used in 'config-write' mode writes a config file with default values"
	)

	return parser.parse_args()