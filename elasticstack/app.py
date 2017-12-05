import os
import argparse
import configparser

from printUtil import *
import fileSearcher
import fileParser

from FILE_FILTERS import FILE_FILTERS
from PARSER_CONF import PARSER_CONF

default_data_path = os.path.normpath(os.path.join(os.getcwd(), "..", "data"))
default_save_path = os.path.normpath(os.path.join(os.getcwd(), "..", "data_elasticstack"))

_indexCounter = 1

def parseFiles(dataFiles, savePath):

	global _indexCounter
	for f in dataFiles:
		print colorTab(YELLOW) + colorText("Parsing %s..." % f, YELLOW)
		_indexCounter = fileParser.parseDataFile(f, savePath, PARSER_CONF, _indexCounter, FILE_FILTERS["included_timestamp"])

def parseFileElastic(dataFiles):
	for f in dataFiles:
		print colorTab(YELLOW) + colorText("Parsing %s..." % f, YELLOW)
		fileParser.parseDataFileSendElastic(f, PARSER_CONF)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Parse data files and write them as files capable of being sent to elasticsearch. Alternetavely send them directly to elasticsearch",
	)
	parser.add_argument("mode", 
		choices=["parse", "parse-elastic", "list", "impossible-timestamps", "noop", "config-write-default", "config-write", "config-list"]
	)
	parser.add_argument("-d", "--data-path", default="../data", 
		help="Relative path to the folder holding the data. Defaults to '../data'")
	parser.add_argument("-s", "--save-path", default="../data", 
		help="Relative path to the folder where the script should save parsed data. Defaults to '../data_elasticstack'")
	parser.add_argument("-c", "--config", default="config.cfg",
		help="Relative path to the configuration file. Defaults to 'config.cfg'")
	parser.add_argument("-v", "--verbose", action="count",
		help="With -v each file filtered will be shown. With -vv both files filtered and passed will be shown")
	parser.add_argument("--config-save-path", default="config.cfg",
		help="Relative path of where to save the newly created configuration file. Defaults to 'config.cfg'")
	parser.add_argument("--default-config", action="store_true",
		help="If set will use a default config object instead of reading one from a file")

	args = parser.parse_args()
	args.data_path = os.path.normpath(os.path.join(os.getcwd(), args.data_path))
	args.save_path = os.path.normpath(os.path.join(os.getcwd(), args.save_path))

	try:
		config = configparser.Config(args.config, args.default_config)
	except configparser.ConfigError as e:
		if not (args.mode == "config-write" or args.mode == "config-write-default"):
			raise e

	dataFiles = fileSearcher.getDataFiles(args.data_path)
	filteredDataFiles = fileSearcher.filterDataFiles(dataFiles, PARSER_CONF, config, (args.verbose > 0), (args.verbose > 1))

	print colorTab(CYAN)
	print colorTab(CYAN) + colorText("Found %d total files" % len(dataFiles), CYAN)
	print colorTab(CYAN) + colorText("Filtered %d files" % (len(dataFiles) - len(filteredDataFiles)), CYAN)
	print colorTab(CYAN) + colorText("Left with %d files" % len(filteredDataFiles), CYAN)
	print colorTab(CYAN)

	if args.mode == "parse":
		parseFiles(filteredDataFiles, args.save_path)
		print colorTab(CYAN) + colorText("Total files found: %d" % len(dataFiles))
		print colorTab(CYAN) + colorText("Total filtered files: %d" % (len(dataFiles) - len(filteredDataFiles)), RED)
		print colorTab(CYAN) + colorText("Total parsed files: %d" % len(filteredDataFiles), CYAN)

	elif args.mode == "parse-elastic":
		parseFileElastic(filteredDataFiles)
		print colorTab(CYAN) + colorText("Total files found: %d" % len(dataFiles))
		print colorTab(CYAN) + colorText("Total filtered files: %d" % (len(dataFiles) - len(filteredDataFiles)), RED)
		print colorTab(CYAN) + colorText("Total parsed files: %d" % len(filteredDataFiles), CYAN)

	elif args.mode == "impossible-timestamps":
		for f in filteredDataFiles:
			t1 = fileParser.parseDataFileHead(f, PARSER_CONF).getProps()["timestamp"]
			t2 = fileParser.parseDataFileTail(f, PARSER_CONF).getProps()["timestamp"]
			color = GREEN if t1 < t2 else RED
			print colorTab(color) + colorText("%s: %s - %s" % (str(f), t1, t2), color)

	elif args.mode == "list":
		for f in filteredDataFiles:
			print colorTab(GREEN) + colorText("%s" % str(f), GREEN)

	elif args.mode == "config-write":
		configparser.writeConfig(args.config_save_path)
	elif args.mode == "config-write-default":
		configparser.writeConfig(args.config_save_path, True)
	elif args.mode == "config-list":
		print "Configuration file being used:\n\n%s" % config