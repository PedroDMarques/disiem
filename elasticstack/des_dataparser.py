import os
import json

from des_printutil import *
from DataLine import DataLine

import dateutil.parser
try:
	from elasticsearch import Elasticsearch
except:
	pass

def parseFile(df, parser, savePath, maxn=False, cb=None):
	softwareParser = parser[df.getSoftware()]

	# mapping date to file to write in
	outFiles = {}

	with open(df.getAbsolutePath(), "r") as inFile:
		n = 1
		for line in inFile:
			if maxn and n > maxn: break

			# Hack for mcafee
			if df.getSoftware() == "mcafee": line = r"%s" % line

			l = DataLine(line, softwareParser, df.getSoftware(), df.getDevice())
			props = l.getProps()
			
			fh = None

			propDate = dateutil.parser.parse(props["timestamp"])
			folderName = propDate.strftime("%Y-%m-%dT%H")
			if folderName in outFiles:
				fh = outFiles[folderName]

			if not fh:
				savingDir = os.path.normpath(os.path.join(savePath, folderName))
				if not os.path.exists(savingDir):
					os.makedirs(savingDir)

				fh = open(os.path.normpath(os.path.join(savingDir, "%s-%s.txt" % (df.getSoftware(), props["des_device_name"]))), "a")
				outFiles[folderName] = fh

			fh.write(json.dumps(props) + "\n")

			if cb:
				cb(props)

			n += 1

	for f in outFiles: outFiles[f].close()

def parseLines(df, conf, callback, maxn=False, timebase=None, time_chunks=60*30):
	with open(df.getAbsolutePath(), "r") as inFile:
		n = 1
		for line in inFile:
			if maxn and n > maxn:
				break

			# Hack for mcafee
			if df.getSoftware() == "mcafee":
				line = r"%s" % line

			l = DataLine(line, conf[df.getSoftware()], df.getSoftware(), df.getDevice())

			if timebase:
				baseDate = dateutil.parser.parse(timebase)
				lineDate = dateutil.parser.parse(l.getProps()["timestamp"])
				seconds = abs((baseDate-lineDate).total_seconds())
				if seconds > time_chunks:
					continue

			callback(l.getProps())
			
			n += 1

def parseDataFileSendElastic(dataFile, conf):
	es = Elasticsearch()
	
	inFilePath = dataFile.getAbsolutePath()

	with open(inFilePath, "r") as inFile:
		for line in inFile:
			# Hack for mcaffee
			if dataFile.getSoftware() == "mcafee":
				line = r"%s" % line
			
			l = DataLine(line, conf[dataFile.getSoftware()], dataFile.getSoftware(), dataFile.getDevice())
			
			es.index(index="disiem", doc_type="disiem", body=l.getProps())

def parseDataFile(dataFile, savePath, conf, startIndex, timeBase=None):
	savingDirPath = os.path.join(savePath, os.path.dirname(dataFile.getDataPath()))
	if not os.path.exists(savingDirPath):
		print colorTab(YELLOW) + colorText("Create non-existent save folder: %s" % savingDirPath, YELLOW)
		os.makedirs(savingDirPath)

	inFilePath = dataFile.getAbsolutePath()
	outFilePath = os.path.join(savePath, dataFile.getDataPath())

	lineCount = startIndex
	with open(inFilePath, "r") as inFile, open(outFilePath, "w") as outFile:
		for line in inFile:
			try:
				# Hack for mcaffee
				if dataFile.getSoftware() == "mcafee":
					line = r"%s" % line

				l = DataLine(line, conf[dataFile.getSoftware()], dataFile.getSoftware(), dataFile.getDevice())
				
				if timeBase:
					baseDate = dateutil.parser.parse(timeBase)
					lineDate = dateutil.parser.parse(l.getProps()["timestamp"])
					seconds = abs((baseDate-lineDate).total_seconds())
					if seconds > conf["general"]["time_interval"]:
						continue

				toWrite = ('{"index":{"_index":"disiem","_type":"disiem","_id":"%d"}}\n%s\n' %
					(lineCount, json.dumps(l.getProps())))
				
				outFile.write(toWrite)
				lineCount+=1

			except:
				raise
				
	return lineCount

def parseDataFileHead(dataFile, conf):
	with open(dataFile.getAbsolutePath(), "r") as f:
		line = f.readline()
		# Hack for mcaffee
		if dataFile.getSoftware() == "mcafee":
			line = r"%s" % line

		return DataLine(f.readline(), conf[dataFile.getSoftware()], dataFile.getSoftware(), dataFile.getDevice())

def parseDataFileTail(dataFile, conf):
	with open(dataFile.getAbsolutePath(), "r") as f:
		line = tail(f, 1)
		# Hack for mcaffee
		if dataFile.getSoftware() == "mcafee":
			line = r"%s" % line

		return DataLine(line, conf[dataFile.getSoftware()], dataFile.getSoftware(), dataFile.getDevice())


## Stolen from stackoverflow...
## Ain't nobody got time to think about this
def tail( f, lines=20 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 12000
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])