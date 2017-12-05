import os

from printUtil import *
import fileSearcher
import fileParser

from FILE_FILTERS import FILE_FILTERS
from PARSER_CONF import PARSER_CONF

DATA_PATH = os.path.normpath(os.path.join(os.getcwd(), "..", "data"))
SAVE_PATH = os.path.normpath(os.path.join(os.getcwd(), "..", "data_elasticstack_experimental"))

MODE = "parse" # possible -> "parse", "list", "impossible-timestamps"

_indexCounter = 1

def parseFiles(dataFiles):

	global _indexCounter
	for f in filteredDataFiles:
		print colorTab(YELLOW) + colorText("Parsing %s..." % f, YELLOW)
		_indexCounter = fileParser.parseDataFile(f, SAVE_PATH, PARSER_CONF, _indexCounter, FILE_FILTERS["included_timestamp"])

if __name__ == "__main__":
	dataFiles = fileSearcher.getDataFiles(DATA_PATH)
	filteredDataFiles = fileSearcher.filterDataFiles(dataFiles, PARSER_CONF, FILE_FILTERS)

	print colorTab(CYAN)
	print colorTab(CYAN) + colorText("Found %d total files" % len(dataFiles), CYAN)
	print colorTab(CYAN) + colorText("Filtered %d files" % (len(dataFiles) - len(filteredDataFiles)), CYAN)
	print colorTab(CYAN) + colorText("Left with %d files" % len(filteredDataFiles), CYAN)
	print colorTab(CYAN)

	if MODE == "parse":
		parseFiles(filteredDataFiles)
		print colorTab(CYAN) + colorText("Total files found: %d" % len(dataFiles))
		print colorTab(CYAN) + colorText("Total filtered files: %d" % (len(dataFiles) - len(filteredDataFiles)), RED)
		print colorTab(CYAN) + colorText("Total parsed files: %d" % len(filteredDataFiles), CYAN)

	elif MODE == "impossible-timestamps":
		for f in filteredDataFiles:
			t1 = fileParser.parseDataFileHead(f, PARSER_CONF).getProps()["timestamp"]
			t2 = fileParser.parseDataFileTail(f, PARSER_CONF).getProps()["timestamp"]
			color = GREEN if t1 < t2 else RED
			print colorTab(color) + colorText("%s: %s - %s" % (str(f), t1, t2), color)

	elif MODE == "list":
		for f in filteredDataFiles:
			print colorTab(GREEN) + colorText("%s" % str(f), GREEN)