import argparse

def parseArgs():
	parser = argparse.ArgumentParser(
		description="Parse amadeus data files, and either write them to disk parsed, or send them directly to elasticsearch"
	)
	
	parser.add_argument("-v", "--verbose", action="count",
		help="With -v each file filtered will be shown. With -vv both files filtered and passed will be shown")
	
	parser.add_argument("mode", 
		choices=["write", "send", "list", "impossible-timestamps", "noop", "config-write", "config-list", "reset-elasticsearch", "output"]
	)

	parser.add_argument("-c", "--config", default="config.cfg", dest="config_location",
		help="Relative path to the configuration file. If used in 'config-write' mode, dictates the file to write to. Defaults to 'config.cfg'"
	)
	
	parser.add_argument("--default-config", action="store_true",
		help="If set will use a default config object instead of reading one from a file. If used in 'config-write' mode writes a config file with default values"
	)

	parser.add_argument("--one-file",
		help="Specify the location of a specific data file to work on. This path should be relative to the 'data_location' config value"
	)

	parser.add_argument("-n", "--number-lines", default=1, type=int,
		help="When using in 'output' mode specifies the number of lines per file that should be outputed"
	)

	return parser.parse_args()