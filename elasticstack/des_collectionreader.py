import os
import json

class CollectionReader(object):
	def __init__(self, filePath):
		self.filePath = filePath
		self.props = {}
		self.readFile()

	def getProps(self):
		return self.props

	def setProps(self, props):
		self.props = props

	def writeFile(self):
		with open(self.filePath, "w") as f:
			for key in self.props:
				f.write("%s=%s\n" % (str(key), str(self.props[key])))

	def readFile(self):
		self.props = {}
		try:
			with open(self.filePath, "r") as f:
				for line in f:
					key, value = line.split("=")
					self.props[key] = value[:-1]
		except IOError:
			pass

def commitFileCollected(metaPath, fileDesc):
	with open(os.path.join(metaPath, "meta_filesCollected"), "a") as f:
		f.write(fileDesc + "\n")

def hasFileBeenCollected(metaPath, fileDesc):
	try:
		with open(os.path.join(metaPath, "meta_filesCollected"), "r") as f:
			for line in f:
				if line[:-1] == fileDesc:
					return True
	except IOError:
		return False

	return False


def collectFile(collectionPath, hourPath, filePath, software, device, fh):
	if hasFileBeenCollected(collectionPath, filePath):
		return False

	alerts = 0
	srcBytes = 0
	dstBytes = 0
	totalBytes = 0
	srcPackets = 0
	dstPackets = 0
	totalPackets = 0
	sumSeverityLevel = 0
	maxSeverityLevel = None
	minSeverityLevel = None
	
	protocol = {}
	sourceZone = {}
	destinationZone = {}
	application = {}
	cat = {}
	sessionEndReason = {}
	eventType = {}
	httpStatus = {}

	for line in fh:
		alerts += 1
		
		lineProps = json.loads(line)

		iProtocol = lineProps.get("protocol")
		if type(iProtocol) is str or type(iProtocol) is unicode:
			protocol[iProtocol] = protocol.get(iProtocol, 0) + 1
		else:
			protocol["desUnknown"] = protocol.get("desUnknown", 0) + 1

		if software == "pan":
			iSrcBytes = lineProps.get("des_src_bytes")
			if (type(iSrcBytes) is str or type(iSrcBytes) is unicode) and iSrcBytes.isdigit(): srcBytes += int(iSrcBytes)

			iDstBytes = lineProps.get("des_dst_bytes")
			if (type(iDstBytes) is str or type(iDstBytes) is unicode) and iDstBytes.isdigit(): dstBytes += int(iDstBytes)

			iTotalBytes = lineProps.get("des_total_bytes")
			if (type(iTotalBytes) is str or type(iTotalBytes) is unicode) and iTotalBytes.isdigit(): totalBytes += int(iTotalBytes)

			iSrcPackets = lineProps.get("srcPackets")
			if (type(iSrcPackets) is str or type(iSrcPackets) is unicode) and iSrcPackets.isdigit(): srcPackets += int(iSrcPackets)

			iDstPackets = lineProps.get("dstPackets")
			if (type(iDstPackets) is str or type(iDstPackets) is unicode) and iDstPackets.isdigit(): dstPackets += int(iDstPackets)

			iTotalPackets = lineProps.get("totalPackets")
			if (type(iTotalPackets) is str or type(iTotalPackets) is unicode) and iTotalPackets.isdigit(): totalPackets += int(iTotalPackets)

			iSourceZone = lineProps.get("SourceZone")
			if type(iSourceZone) is str or type(iSourceZone) is unicode:
				sourceZone[iSourceZone] = sourceZone.get(iSourceZone, 0) + 1
			else:
				sourceZone["desUnknown"] = sourceZone.get("desUnknown", 0) + 1

			iDestinationZone = lineProps.get("DestinationZone")
			if type(iDestinationZone) is str or type(iDestinationZone) is unicode:
				destinationZone[iDestinationZone] = destinationZone.get(iDestinationZone, 0) + 1
			else:
				destinationZone["desUnknown"] = destinationZone.get("desUnknown", 0) + 1

			iApplication = lineProps.get("Application")
			if type(iApplication) is str or type(iApplication) is unicode:
				application[iApplication] = application.get(iApplication, 0) + 1
			else:
				application["desUnknown"] = application.get("desUnknown", 0) + 1

			iCat = lineProps.get("cat")
			if type(iCat) is str or type(iCat) is unicode:
				cat[iCat] = cat.get(iCat, 0) + 1
			else:
				cat["desUnknown"] = cat.get("desUnknown", 0) + 1

			iSessionEndReason = lineProps.get("SessionEndReason")
			if type(iSessionEndReason) is str or type(iSessionEndReason) is unicode:
				sessionEndReason[iSessionEndReason] = sessionEndReason.get(iSessionEndReason, 0) + 1
			else:
				sessionEndReason["desUnknown"] = sessionEndReason.get("desUnknown", 0) + 1

		elif software == "ciscoasa":

			iSeverityLevel = lineProps.get("syslog_severity_code")
			if (type(iSeverityLevel) is str or type(iSeverityLevel) is unicode) and iSeverityLevel.isdigit():
				isl = int(iSeverityLevel)
				sumSeverityLevel += isl
				if isl > maxSeverityLevel or not maxSeverityLevel:
					maxSeverityLevel = isl
				if isl < minSeverityLevel or not minSeverityLevel:
					minSeverityLevel = isl
				
		elif software == "suricata":

			iEventType = lineProps.get("event_type")
			if type(iEventType) is str or type(iEventType) is unicode:
				eventType[iEventType] = eventType.get(iEventType, 0) + 1
			else:
				eventType["desUnknown"] = eventType.get("desUnknown", 0) + 1

			iHTTPStatus = lineProps.get("http.status")
			if type(iHTTPStatus) is str or type(iHTTPStatus) is unicode:
				httpStatus[iHTTPStatus] = httpStatus.get(iHTTPStatus, 0) + 1
			else:
				httpStatus["desUnknown"] = httpStatus.get("desUnknown", 0) + 1

	savingDir = os.path.join(collectionPath, hourPath)
	if not os.path.exists(savingDir):
		os.makedirs(savingDir)

	reader = CollectionReader(os.path.join(savingDir, "%s-%s.txt" % (software, device)))
	
	readerProps = reader.getProps()
	readerProps["alerts"] = int(readerProps.get("alerts", 0)) + alerts
	for k in protocol:
		readerProps["protocol_%s" % k] = int(readerProps.get("protocol_%s" % k, 0)) + protocol[k]

	if software == "pan":
		readerProps["srcBytes"] = int(readerProps.get("srcBytes", 0)) + srcBytes
		readerProps["dstBytes"] = int(readerProps.get("dstBytes", 0)) + dstBytes
		readerProps["totalBytes"] = int(readerProps.get("totalBytes", 0)) + totalBytes
		readerProps["srcPackets"] = int(readerProps.get("srcPackets", 0)) + srcPackets
		readerProps["dstPackets"] = int(readerProps.get("dstPackets", 0)) + dstPackets
		readerProps["totalPackets"] = int(readerProps.get("totalPackets", 0)) + totalPackets
		for k in sourceZone:
			readerProps["sourceZone_%s" % k] = int(readerProps.get("sourceZone_%s" % k, 0)) + sourceZone[k]
		for k in destinationZone:
			readerProps["destinationZone_%s" % k] = int(readerProps.get("destinationZone_%s" % k, 0)) + destinationZone[k]
		for k in application:
			readerProps["application_%s" % k] = int(readerProps.get("application_%s" % k, 0)) + application[k]
		for k in cat:
			readerProps["cat_%s" % k] = int(readerProps.get("cat_%s" % k, 0)) + cat[k]
		for k in sessionEndReason:
			readerProps["sessionEndReason_%s" % k] = int(readerProps.get("sessionEndReason_%s" % k, 0)) + sessionEndReason[k]

	elif software == "ciscoasa":
		readerProps["sumSeverityLevel"] = int(readerProps.get("sumSeverityLevel", 0)) + sumSeverityLevel
		minimum = readerProps.get("minSeverityLevel", None)
		if minSeverityLevel < minimum or not minimum:
			readerProps["minSeverityLevel"] = minSeverityLevel
		maximum = readerProps.get("maxSeverityLevel", None)
		if maxSeverityLevel < maximum or not maximum:
			readerProps["maxSeverityLevel"] = maxSeverityLevel

	elif software == "suricata":
		for k in eventType:
			readerProps["eventType_%s" % k] = int(readerProps.get("eventType_%s" % k, 0)) + eventType[k]
		for k in httpStatus:
			readerProps["httpStatus_%s" % k] = int(readerProps.get("httpStatus_%s" % k, 0)) + httpStatus[k]

	reader.setProps(readerProps)
	reader.writeFile()

	commitFileCollected(collectionPath, filePath)
	
	return True