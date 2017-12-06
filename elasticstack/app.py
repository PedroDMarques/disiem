import os

import des_argparser
import des_configparser
import des_filesearcher
import des_dataparser

from printUtil import *


from PARSER_CONF import PARSER_CONF

_indexCounter = 1

try:
	from elasticsearch import Elasticsearch
except:
	pass

def _configWrite(args):
	des_configparser.writeConfigFile(args.config_location, args.default_config)

def _configList(args, config):
	print config

def _write(args, config):
	print colorTab(RED) + colorText("Currently out of comission. Check back later...", RED)

def _send(args, config):
	files, filtered = getDataFiles(args, config)
	for df in filtered:
		print colorTab(YELLOW) + colorText("%s... processing and sending" % df, YELLOW)
		des_dataparser.parseDataFileSendElastic(df, PARSER_CONF)

def _list(args, config):
	files, filtered = getDataFiles(args, config)
	
	print colorTab(YELLOW)
	print colorTab(YELLOW) + colorText("Listing files...", YELLOW)
	print colorTab(YELLOW)

	for df in filtered:
		print colorTab(YELLOW) + colorText(df, YELLOW)

	printDataFileCounts(len(files), len(filtered))

def _impossibleTimestamps(args, config):
	files, filtered = getDataFiles(args, config)

	print colorTab(YELLOW)
	print colorTab(YELLOW) + colorText("Listing files...", YELLOW)
	print colorTab(YELLOW)

	for df in filtered:
			t1 = fileParser.parseDataFileHead(df, PARSER_CONF).getProps()["timestamp"]
			t2 = fileParser.parseDataFileTail(df, PARSER_CONF).getProps()["timestamp"]
			color = GREEN if t1 < t2 else RED
			print colorTab(color) + colorText("%s: %s - %s" % (df, t1, t2), color)

	printDataFileCounts(len(files), len(filtered))

def _noop(args, config):
	pass

def _resetElasticsearch(args, config):
	es = Elasticsearch()
	es.indices.delete(index="_all", ignore=[400, 404])

def getDataFiles(args, config):
	dataFiles = des_filesearcher.getDataFiles(config.getOption("data_location"))
	filtered = des_filesearcher.filterDataFiles(dataFiles, PARSER_CONF, config,
		verboseFilter=(args.verbose > 0),
		verbosePass=(args.verbose > 1)
	)

	return (dataFiles, filtered)

def printDataFileCounts(lenFiles, lenFiltered):
	print colorTab(CYAN)
	print colorTab(CYAN) + colorText("Found %d total files" % lenFiles, CYAN)
	print colorTab(CYAN) + colorText("Filtered %d files" % (lenFiles - lenFiltered), CYAN)
	print colorTab(CYAN) + colorText("Left with %d files" % lenFiltered, CYAN)
	print colorTab(CYAN)

if __name__ == "__main__":
	
	args = des_argparser.parseArgs()

	if args.mode == "config-write": _configWrite(args)
	else:
		config = des_configparser.Configuration(args.config_location, args.default_config)
		
		if args.mode == "config-list": _configList(args, config)
		elif args.mode == "write": _write(args, config)
		elif args.mode == "send": _send(args, config)
		elif args.mode == "list": _list(args, config)
		elif args.mode == "impossible-timestamps": _impossibleTimestamps(args, config)
		elif args.mode == "noop": _noop(args, config)
		elif args.mode == "reset-elasticsearch": _resetElasticsearch(args, config)

"""
def parseFiles(dataFiles, savePath):

	global _indexCounter
	for f in dataFiles:
		print colorTab(YELLOW) + colorText("Parsing %s..." % f, YELLOW)
		_indexCounter = fileParser.parseDataFile(f, savePath, PARSER_CONF, _indexCounter, FILE_FILTERS["included_timestamp"])

def parseFileElastic(dataFiles):
	for f in dataFiles:
		print colorTab(YELLOW) + colorText("Parsing %s..." % f, YELLOW)
		fileParser.parseDataFileSendElastic(f, PARSER_CONF)
"""