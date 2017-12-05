import os
from printUtil import *
from DataFile import DataFile

import fileParser

def getDataFiles(basePath, cyclePath=""):
	nextPath = os.path.join(basePath, cyclePath)

	dataFiles = []
	for fname in os.listdir(nextPath):
		newCyclePath = os.path.join(cyclePath, fname)
		fullPath = os.path.join(basePath, newCyclePath)

		if os.path.isdir(fullPath):
			dataFiles += getDataFiles(basePath, newCyclePath)
		else:
			dataFiles.append(DataFile(basePath, newCyclePath))

	return dataFiles

def filterDataFiles(files, parserConf, filters=dict()):
	filteredFiles = []
	for f in files:
		# Filter by software
		if f.getSoftware() in filters["ignore_software"]:
			print colorTab(RED) + colorText(str(f)+ " --- Filtered based on software [%s]" % f.getSoftware(), RED)
			continue

		# Filter by device
		if f.getDevice() in filters["ignore_device"]:
			print colorTab(RED) + colorText(str(f) + " --- Filtered based on device [%s]" % f.getDevice(), RED)
			continue

		# Filter by file names
		if f.getFileName() in filters["ignore_file_names"]:
			print colorTab(RED) + colorText(str(f) + " --- Filtered based on file name [%s]" % f.getFileName(), RED)
			continue

		# Filter by file extensions
		if f.getFileExt() in filters["ignore_file_ext"]:
			print colorTab(RED) + colorText(str(f) + " --- Filtered based on file extension [%s]" % f.getFileExt(), RED)
			continue

		# Filter by file size
		if filters["min_size"]:
			if f.getFileSize() < filters["min_size"]:
				print colorTab(RED) + colorText(str(f) + " --- Filtered based on file size [%d]" % f.getFileSize(), RED)
				continue

		if filters["max_size"]:
			if f.getFileSize() > filters["max_size"]:
				print colorTab(RED) + colorText(str(f) + " --- Filtered based on file size [%d]" % f.getFileSize(), RED)
				continue

		# Filter by timestamp
		if filters["included_timestamp"]:
			t1 = fileParser.parseDataFileHead(f, parserConf).getProps()["timestamp"]
			t2 = fileParser.parseDataFileTail(f, parserConf).getProps()["timestamp"]

			if not (t1 < filters["included_timestamp"] < t2):
				print colorTab(RED) + colorText(str(f) + " --- Filtered based on timestamp [%s - %s]" % (t1, t2), RED)
				continue

		print colorTab(GREEN) + colorText(f.getDataPath(), GREEN)
		filteredFiles.append(f)

	return filteredFiles