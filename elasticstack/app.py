import os
import time

import des_argparser
import des_configparser
import des_filesearcher
import des_dataparser
from des_printutil import *

from DataFile import DataFile
from des_BulkIterator import BulkIterator

from PARSER_CONF import PARSER_CONF
from CREATE_INDEX import CREATE_INDEX

_indexCounter = 1

global es
try:
	import elasticsearch
	import elasticsearch.helpers
	from elasticsearch import Elasticsearch
	global es
	es = Elasticsearch()
except:
	pass

def _configWrite(args):
	des_configparser.writeConfigFile(args.config_location, args.default_config)

def _configList(args, config):
	print config

def _list(files, filtered, args, config):
	print colorTab(YELLOW)
	print colorTab(YELLOW) + colorText("Listing files...", YELLOW)
	print colorTab(YELLOW)

	for df in filtered:
		print colorTab(YELLOW) + colorText(df, YELLOW)

	printDataFileCounts(len(files), len(filtered))

def _impossibleTimestamps(files, filtered, args, config):
	print colorTab(YELLOW)
	print colorTab(YELLOW) + colorText("Impossible timestamps...", YELLOW)
	print colorTab(YELLOW)

	for df in filtered:
			t1 = des_dataparser.parseDataFileHead(df, PARSER_CONF).getProps()["timestamp"]
			t2 = des_dataparser.parseDataFileTail(df, PARSER_CONF).getProps()["timestamp"]
			color = GREEN if t1 < t2 else RED
			print colorTab(color) + colorText("%s: %s - %s" % (df, t1, t2), color)

	printDataFileCounts(len(files), len(filtered))

def _output(files, filtered, args, config):
	def cb(line):
		print colorTab(YELLOW) + colorText(line, YELLOW)

	if not args.number_lines:
		args.number_lines = 1

	for df in filtered:
		parseLines(args, config, df, cb)

def _parse(files, filtered, args, config):
	global nLines
	nLines = 0
	def cb(line):
		global nLines
		nLines += 1

	for df in filtered:
		startTime = time.time()
		print colorLog("info", "Processing... %s" % df)
		
		des_dataparser.parseFile(df, PARSER_CONF, config.getOption("save_location"), maxn=args.number_lines, cb=cb)
		
		elapsedSeconds = round(time.time() - startTime, 3)
		print colorLog("info", "Finished processing, took %s seconds and processed %d lines" % (elapsedSeconds, nLines))
		
		nLines = 0

def _parseSend(files, filtered, args, config):
	nLines = 0
	global es
	def cb(line):
		global es
		nLines += 1

		index = args.es_index if args.es_index else config.getOption("elasticsearch_index")
		es.index(index=index, doc_type="disiem", body=line)

	for df in filtered:
		startTime = time.time()
		print colorLog("info", "Processing... %s" % df)

		des_dataparser.parseFile(df, PARSER_CONF, config.getOption("save_location"), maxn=args.number_lines, cb=cb)

		elapsedSeconds = round(time.time() - startTime, 3)
		print colorLog("info", "Finished processing, took %s seconds and processed %d lines" % (elapsedSeconds, nLines))
		
		nLines = 0

def _sendParsed(args, config):
	global es
	index = args.es_index if args.es_index else config.getOption("elasticsearch_index")

	saveFolder = config.getOption("save_location")
	if not args.specific_files:
		print colorLog("danger", "--specific-files is required for send-parsed. If you wish to send all the folders in the parsed data location, set --specific-files to 'all'")
		return
	
	sendingFolders = os.listdir(saveFolder) if args.specific_files == "all" else args.specific_files.split(",")

	for sf in sendingFolders:
		hourFolder = os.path.join(saveFolder, sf)
		
		if not os.path.isdir(hourFolder):
			continue

		for fname in os.listdir(hourFolder):
			filePath = os.path.join(hourFolder, fname)

			if not os.path.isdir(filePath):
				startTime = time.time()

				print colorLog("info", "Processing... %s" % filePath)
				with open(filePath, "r") as fh:
					elasticsearch.helpers.streaming_bulk(es, BulkIterator(fh, index))

				elapsedSeconds = round(time.time() - startTime, 3)
				print colorLog("info", "Finished processing, took %s seconds" % elapsedSeconds)

def _send(files, filtered, args, config):
	global es
	def cb(line):
		global es
		
		index = args.es_index if args.es_index else config.getOption("elasticsearch_index")
		es.index(index=index, doc_type="disiem", body=line)

	for df in filtered:
		print colorTab(YELLOW) + colorText("%s... processing and sending" % df, YELLOW)
		parseLines(args, config, df, cb)
		print colorTab(YELLOW) + colorText("done", YELLOW)

def _rankParsed(args, config):
	folders = dict()
	topBytes = None
	topDevices = None

	parsedFolder = config.getOption("save_location")
	for hourFolder in os.listdir(parsedFolder):
		p = os.path.join(parsedFolder, hourFolder)
		if os.path.isdir(p):
			totalBytes = 0
			totalDevices = 0
			for fname in os.listdir(p):
				np = os.path.join(p, fname)
				if not os.path.isdir(np):
					totalBytes += os.path.getsize(np)
					totalDevices += 1

			folders[hourFolder] = (totalBytes, totalDevices)
			topBytes = totalBytes if totalBytes > topBytes else topBytes
			topDevices = totalDevices if totalDevices > topDevices else topDevices

	saveLast = []
	for f in folders:
		toPrint = "%s - [%d bytes, %d devices]" % (f, folders[f][0], folders[f][1])
		wait = False
		if folders[f][1] >= topDevices:
			toPrint += " | top devices"
			wait = True
		if folders[f][0] >= topBytes:
			toPrint += " | top bytes"
			wait = True

		if wait:
			saveLast.append(toPrint)
		else:
			print colorLog("danger", toPrint)

	for p in saveLast:
		print colorLog("success", p)
		

def _createIndex(args, config):
	global es

	index = args.es_index if args.es_index else config.getOption("elasticsearch_index")
	es.indices.create(index=index, body=CREATE_INDEX)

def _noop(args, config):
	pass

def _deleteIndex(args, config):
	global es

	index = args.es_index if args.es_index else config.getOption("elasticsearch_index")
	es.indices.delete(index=index, ignore=[400, 404])

def _resetElasticsearch(args, config):
	global es

	index = args.es_index if args.es_index else config.getOption("elasticsearch_index")
	es.indices.delete(index=index, ignore=[400, 404])

def getDataFiles(args, config):
	dataFiles = des_filesearcher.getDataFiles(config.getOption("data_location"))
	filtered = des_filesearcher.filterDataFiles(dataFiles, PARSER_CONF, config,
		verboseFilter=(args.verbose > 1),
		verbosePass=(args.verbose > 2)
	)

	if args.include_files:
		for f in args.include_files.split(","):
			if f not in [x.getDataPath() for x in filtered]:
				filtered.append(DataFile(config.getOption("data_location"), os.path.normpath(f)))

	return (dataFiles, filtered)

linesParsed = 0

def parseLines(args, config, df, cb):
	global linesParsed
	startTime = time.time()

	def overCb(line):
		global linesParsed
		linesParsed += 1
		cb(line)

	des_dataparser.parseLines(
		df,
		PARSER_CONF,
		overCb,
		maxn=args.number_lines,
		timebase=config.getOption("data_file_includes_timestamp"),
		time_chunks=config.getOption("time_chunks")
	)

	endTime = time.time()

	if args.verbose > 0:
		print colorTab(YELLOW) + colorText("Processed %d lines for latest data file" % linesParsed, YELLOW)
		print colorTab(YELLOW) + colorText("Took %s seconds to process" % round(endTime - startTime, 3), YELLOW)

	linesParsed = 0

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
		elif args.mode == "noop": _noop(args, config)
		elif args.mode == "reset-elasticsearch": _resetElasticsearch(args, config)
		elif args.mode == "create-index": _createIndex(args, config)
		elif args.mode == "delete-index": _deleteIndex(args, config)
		elif args.mode == "rank-parsed": _rankParsed(args, config)
		elif args.mode == "send-parsed": _sendParsed(args, config)

		else:
			if args.specific_files:
				df = [DataFile(config.getOption("data_location"), os.path.normpath(x)) for x in args.specific_files.split(",")]
				files, filtered = df, df
			else:
				files, filtered = getDataFiles(args, config)

			if args.mode == "parse": _parse(files, filtered, args, config)
			elif args.mode == "send": _send(files, filtered, args, config)
			elif args.mode == "parse-send" or args.mode == "send-parse": _parseSend(files, filtered, args, config)
			elif args.mode == "list": _list(files, filtered, args, config)
			elif args.mode == "impossible-timestamps": _impossibleTimestamps(files, filtered, args, config)
			elif args.mode == "output": _output(files, filtered, args, config)

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