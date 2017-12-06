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

def printFilter(df, reason, p1=None, p2=None):
	if reason == "software":
		print colorTab(RED) + colorText("%s --- Filtered based on software [%s]" % (df, df.getSoftware()), RED)
	elif reason == "device":
		print colorTab(RED) + colorText("%s --- Filtered based on device [%s]" % (df, df.getDevice()), RED)
	elif reason == "name":
		print colorTab(RED) + colorText("%s --- Filtered based on file name [%s]" % (df, df.getFileName()), RED)
	elif reason == "ext":
		print colorTab(RED) + colorText("%s --- Filtered based on file extension [%s]" % (df, df.getFileExt()), RED)
	elif reason == "min_size":
		print colorTab(RED) + colorText("%s --- Filtered based on file size [%d]" % (df, df.getFileSize()), RED)
	elif reason == "max_size":
		print colorTab(RED) + colorText("%s --- Filtered based on file size [%d]" % (df, df.getFileSize()), RED)
	elif reason == "included_timestamp":
		print colorTab(RED) + colorText("%s --- Filtered based on timestamp [%s - %s]" % (df, p1, p2), RED)

def printPass(dataFile):
	print colorTab(GREEN) + colorText(dataFile, GREEN)

def filterDataFiles(files, parserConf, config, **kwargs):
	verboseFilter = kwargs["verboseFilter"] if "verboseFilter" in kwargs else False
	verbosePass = kwargs["verbosePass"] if "verbosePass" in kwargs else False

	filteredFiles = []
	for df in files:
		
		if df.getSoftware() in config.getOption("ignore_software"):
			if verboseFilter: printFilter(df, "software")
			continue
		
		if df.getDevice() in config.getOption("ignore_device"):
			if verboseFilter: printFilter(df, "device")			
			continue
		
		if df.getFileName() in config.getOption("ignore_file_name"):
			if verboseFilter: printFilter(df, "name")
			continue
		
		if df.getFileExt() in config.getOption("ignore_file_extension"):
			if verboseFilter: printFilter(df, "ext")
			continue
		
		if config.getOption("min_data_file_size"):
			if df.getFileSize() < config.getOption("min_data_file_size"):
				if verboseFilter: printFilter(df, "min_size")
				continue
		
		if config.getOption("max_data_file_size"):
			if df.getFileSize() > config.getOption("max_data_file_size"):
				if verboseFilter: printFilter(df, "max_size")
				continue
		
		if config.getOption("data_file_includes_timestamp"):
			t1 = fileParser.parseDataFileHead(df, parserConf).getProps()["timestamp"]
			t2 = fileParser.parseDataFileTail(df, parserConf).getProps()["timestamp"]
			if not (t1 < config.getOption("data_file_includes_timestamp") < t2):
				if verboseFilter: printFilter(df, "data_file_includes_timestamp", t1, t2)
				continue

		filteredFiles.append(df)
		if verbosePass: printPass(df)

	return filteredFiles