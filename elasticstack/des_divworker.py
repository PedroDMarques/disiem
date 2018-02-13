import os
import datetime
import dateutil.parser

def commitFileCollected(metaPath, fileDesc, metaName="meta_hoursDivCompared"):
	with open(os.path.join(metaPath, metaName), "a") as f:
		f.write(fileDesc + "\n")

def hasFileBeenCollected(metaPath, fileDesc, metaName="meta_hoursDivCompared"):
	try:
		with open(os.path.join(metaPath, metaName), "r") as f:
			for line in f:
				if line[:-1] == fileDesc:
					return True
	except IOError:
		return False

	return False

def getDivFiles(hourPath):
	for fname in os.listdir(hourPath):
		if fname.split("-")[0] != "meta":
			
			softwares = fname.split("-")
			data = dict()
			with open(os.path.join(hourPath, fname), "r") as fh:
				for line in fh:
					try:
						lineS = line.split("\n")[0].split(",")
						
						pair = lineS[0]
						software = lineS[1]
						timestamp = lineS[-1]
						if pair not in data: data[pair] = {s: [] for s in softwares}
						data[pair][software].append(timestamp)
					except:
						print "error on:"
						print lineS
						pass

			yield (softwares, data)

def compareDiv(collectionLocation, hourPath):
	if hasFileBeenCollected(collectionLocation, hourPath):
		return False

	counts = dict()
	for softwares, data in getDivFiles(hourPath):
		softwaresName = ",".join(softwares)

		intervalCounts = {x: 0 for x in [1,2,5,10,20,30,60,120,300,600,1200,1800,2700]}
		for pair in data:
			softwareList = data[pair].keys()
			chosenSoftware, restSoftwares = softwareList[0], softwareList[1:]
			for a in data[pair][chosenSoftware]:
				countIntervals = {x: False for x in [1,2,5,10,20,30,60,120,300,600,1200,1800,2700]}

				for otherSof in restSoftwares:
					for b in data[pair][otherSof]:
						
						if type(a) is not datetime.datetime:
							a = dateutil.parser.parse(a)
						if type(b) is not datetime.datetime:
							b = dateutil.parser.parse(b)
						
						seconds = (a-b).total_seconds()
						for interval in countIntervals:
							countIntervals[interval] = (seconds <= interval)

				for interval in countIntervals:
					if countIntervals[interval]: intervalCounts[interval] = intervalCounts.get(interval, 0) + 1

		for interval in intervalCounts:
			countName = "%s,%d" % (softwaresName, interval)
			counts[countName] = intervalCounts[interval]
			

	saveFile = os.path.join(hourPath, "meta-lentimeintervals")
	with open(saveFile, "w") as fh:
		for count in counts:
			if counts[count] > 0:
				print "Found %d matches for %s" % (counts[count], count)

			fh.write("%s=%d\n" % (count, counts[count]))

	commitFileCollected(collectionLocation, hourPath)
	return True