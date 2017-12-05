import os

class DataFile(object):
	def __init__(self, basePath, dataPath):
		"""
		Constructor for the DataFile
		@param {String} basePath The base path where the data is found
		@param {String} dataPath The relativa path of where this file is found, relative to the base path provided
		"""
		self.basePath = basePath
		self.dataPath = dataPath
		self.software = dataPath.split("\\")[0]
		self.device = dataPath.split("\\")[1]
		self.fileName = dataPath.split("\\")[-1]
		self.fileExt = self.fileName.split(".")[-1]
		if self.fileExt == self.fileName:
			self.fileExt = None

	def getBasePath(self):
		return self.basePath

	def getDataPath(self):
		return self.dataPath
	
	def getAbsolutePath(self):
		return os.path.normpath(os.path.join(self.basePath, self.dataPath))

	def getSoftware(self):
		return self.software

	def getDevice(self):
		return self.device

	def getFileName(self):
		return self.fileName

	def getFileExt(self):
		return self.fileExt

	def getFileSize(self):
		return os.path.getsize(self.getAbsolutePath())

	def __repr__(self):
		return "%s [%d bytes]" % (self.getDataPath(), self.getFileSize())

	def __str__(self):
		return "%s [%d bytes]" % (self.getDataPath(), self.getFileSize())