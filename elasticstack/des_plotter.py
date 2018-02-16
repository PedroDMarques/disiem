import os
from des_collectionreader import CollectionReader

import dateutil.parser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
sns.set()

COLORS = {
	"div-lines-ciscoasa-pan": {
		"ciscoasa": "#3366CC",
		"pan": "#DC3912",
		"ciscoasa,pan": "#FF9900",
		"ciscoasa,pan,1": "#109618",
		"ciscoasa,pan,2": "#990099",
		"ciscoasa,pan,5": "#3B3EAC",
		"ciscoasa,pan,10": "#0099C6",
		"ciscoasa,pan,20": "#DD4477",
		"ciscoasa,pan,30": "#66AA00",
		"ciscoasa,pan,60": "#B82E2E",
		"ciscoasa,pan,120": "#316395",
		"ciscoasa,pan,300": "#994499",
		"ciscoasa,pan,600": "#22AA99",
		"ciscoasa,pan,1200": "#AAAA11",
		"ciscoasa,pan,1800": "#6633CC",
		"ciscoasa,pan,2700": "#E67300",
	},
	"div-lines": {
		"ciscoasa": "#3366CC",
		"pan": "#DC3912",
		"suricata": "#FF9900",
		"ciscoasa,pan": "#109618",
		"ciscoasa,suricata": "#990099",
		"pan,suricata": "#3B3EAC",
		"ciscoasa,pan,suricata": "#0099C6",
		"bro,pan": "#DD4477",
		"bro": "#66AA00",
		"bro,ciscoasa,pan": "#B82E2E",
		"bro,ciscoasa": "#316395",
		"ciscoasa,ciscovpn": "#994499",
		"ciscovpn": "#22AA99",
		"mcafee": "#AAAA11",
	},
	"softwares": {
		"suricata": "#3366CC",
		"ciscoasa": "#DC3912",
		"pan": "#FF9900",
		"ciscovpn": "#109618",
		"bro": "#990099",
		"mcafee": "#3B3EAC",
	},
	"protocols": {
		"tcp": "#3366CC",
		"udp": "#DC3912",
		"desUnknown": "#FF9900",
		"47": "#109618",
		"gre": "#990099",
		"icmp": "#3B3EAC",
		"ipsec": "#0099C6",
		"63": "#DD4477",
		"egp": "#66AA00",
		"hopopt": "#B82E2E",
		"etherip": "#316395",
		"ipv6": "#994499",
	},
	"pan-devices": {
		"mucfwo301a": "#3366CC",
		"mucfwp308a": "#DC3912",
		"mucfwp3100a": "#FF9900",
		"mucfwp311a": "#109618",
		"sydfwo300a": "#990099",
		"frafwp300a": "#3B3EAC",
		"miafwo300a": "#0099C6",
		"atlfwo300a": "#DD4477",
		"10.68.15.53": "#66AA00",
		"sinfwo302a": "#B82E2E",
		"mucfwp608a": "#316395",
		"madfwo301a": "#994499",
		"dfwfwo300a": "#22AA99",
		"mucfwp322a": "#AAAA11",
		"172.22.137.53": "#6633CC",
		"selfwo300": "#E67300",
		"ncefwt1": "#8B0707",
		"172.16.1.63": "#329262",
		"mucfwp373a": "#5574A6",
		"bosfwo300a": "#3B3EAC",
		"10.68.15.54": "#3366CC",
		"blrfwo300a": "#DC3912",
		"mucfwp393a": "#FF9900",
	},
	"ciscoasa-devices": {
		"mnpfwp41": "#3366CC",
		"mucfwp112": "#DC3912",
		"mucfwp110": "#FF9900",
		"blrfwo01": "#109618",
		"KULFWO01": "#990099",
		"hkgfwo04": "#3B3EAC",
		"atlfwp03": "#0099C6",
		"SYDFWO01": "#DD4477",
		"HKGFWO01": "#66AA00",
	},
	"suricata-devices": {
		"nce": "#3366CC",
		"ncesecids05": "#DC3912",
		"ncesecids06": "#FF9900",
	},
}

def getCollectionFiles(collectionLocation):
	f = []
	for hourFolder in os.listdir(collectionLocation):
		if not os.path.isdir(os.path.join(collectionLocation, hourFolder)):
			continue

		for fname in os.listdir(os.path.join(collectionLocation, hourFolder)):
			fullPath = os.path.join(collectionLocation, hourFolder, fname)
			software, device = fname.split(".txt")[0].split("-")
			f.append((hourFolder, software, device, CollectionReader(fullPath).getProps()))

	return f

def getCollectionDivMeta(collectionLocation):
	f = []
	for hourFolder in os.listdir(collectionLocation):
		if not os.path.isdir(os.path.join(collectionLocation, hourFolder)):
			continue
		
		metaFileName = os.path.join(collectionLocation, hourFolder, "meta-srcdstlen")
		if os.path.exists(metaFileName):
			d = dict()
			with open(metaFileName, "r") as fh:
				for line in fh:
					key, value = line.split("\n")[0].split("=")
					d[key] = int(value)

			f.append([hourFolder, d])

	return f

def getCollectionDivMetaEx(collectionLocation):
	"""
	returns a list of [hourFolder, True if data has timeinvertals information, props]
	"""

	f = []

	for hourFolder in os.listdir(collectionLocation):
		if not os.path.isdir(os.path.join(collectionLocation, hourFolder)):
			continue
		
		for fileName in ["meta-srcdstlen", "meta-lentimeintervals"]:
			metaFileName = os.path.join(collectionLocation, hourFolder, fileName)
			if os.path.exists(metaFileName):
				d = dict()
				with open(metaFileName, "r") as fh:
					for line in fh:
						key, value = line.split("\n")[0].split("=")
						d[key] = int(value)

				f.append([hourFolder, (fileName == "meta-lentimeintervals"), d])

	return f

def plotDataPie(collectionLocation, plot, save=False, saveLocation=""):
	data = {}
	uniqueKeys = set()
	title = "PH:title"

	if plot == "pie-software-alerts": title = "Alert counts by software"
	elif plot == "pie-suricata-alerts": title = "Alert counts by suricata device"
	elif plot == "pie-ciscoasa-alerts": title = "Alert counts by ciscoasa device"
	elif plot == "pie-pan-alerts": title = "Alert counts by pan device"

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if plot == "pie-software-alerts":
			uniqueKeys.add(software)
			alerts = int(props.get("alerts"))
			data[software] = data.get(software, 0) + alerts

		if plot == "pie-suricata-alerts":
			if software != "suricata":
				continue

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[device] = data.get(device, 0) + alerts

		if plot == "pie-ciscoasa-alerts":
			if software != "ciscoasa":
				continue

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[device] = data.get(device, 0) + alerts

		if plot == "pie-pan-alerts":
			if software != "pan":
				continue

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[device] = data.get(device, 0) + alerts

	values = []
	labels = []
	for k in uniqueKeys:
		values.append(data[k])
		labels.append(k)

	plotPie(values, labels, title, save=save, saveLocation=saveLocation)

def plotDataOverTime(collectionLocation, plot, save=False, saveLocation=""):
	data = dict()
	uniqueKeys = set()
	title = "PH:title"

	if plot == "software-alerts": title = "Alerts counts over time by software"
	elif plot == "suricata-alerts": title = "Alert counts over time by suricata devices"
	elif plot == "ciscoasa-alerts": title = "Alert counts over time by ciscoasa devices"
	elif plot == "pan-alerts": title = "Alert counts over time by pan devices"
	elif plot == "device-alerts": title = "Alert counts over time by device"
	elif plot == "suricata-protocol": title = "Suricata alert counts over time by protocol"
	elif plot == "ciscoasa-protocol": title = "Ciscoasa alert counts over time by protocol"
	elif plot == "pan-protocol": title = "Pan alert counts over time by protocol"

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if timestamp not in data:
			data[timestamp] = dict()

		if plot == "software-alerts":
			uniqueKeys.add(software)
			alerts = int(props.get("alerts"))
			data[timestamp][software] = data[timestamp].get(software, 0) + alerts
		
		elif plot == "suricata-alerts":
			if software != "suricata":
				continue 

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[timestamp][device] = data[timestamp].get(device, 0) + alerts

		elif plot == "ciscoasa-alerts":
			if software != "ciscoasa":
				continue

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[timestamp][device] = data[timestamp].get(device, 0) + alerts

		elif plot == "pan-alerts":
			if software != "pan":
				continue

			uniqueKeys.add(device)
			alerts = int(props.get("alerts"))
			data[timestamp][device] = data[timestamp].get(device, 0) + alerts

		elif plot == "device-alerts":
			k = "%s - %s" % (software, device)
			uniqueKeys.add(k)
			alerts = int(props.get("alerts"))
			data[timestamp][k] = data[timestamp].get(k, 0) + alerts

		elif plot == "suricata-protocol":
			if software != "suricata":
				continue

			for k in props:
				if k.split("_")[0] == "protocol":
					uniqueKeys.add(k)
					alerts = int(props.get(k))
					data[timestamp][k] = data[timestamp].get(k, 0) + alerts

		elif plot == "ciscoasa-protocol":
			if software != "ciscoasa":
				continue

			for k in props:
				if k.split("_")[0] == "protocol":
					uniqueKeys.add(k)
					alerts = int(props.get(k))
					data[timestamp][k] = data[timestamp].get(k, 0) + alerts

		elif plot == "pan-protocol":
			if software != "pan":
				continue

			for k in props:
				if k.split("_")[0] == "protocol":
					uniqueKeys.add(k)
					alerts = int(props.get(k))
					data[timestamp][k] = data[timestamp].get(k, 0) + alerts
					

	timestamps = []
	lines = {key: [] for key in uniqueKeys}

	for timestamp in sorted(data.keys()):
		timestamps.append(timestamp)
		for k in lines:
			lines[k].append(data[timestamp].get(k, 0))

	plotOverTime(timestamps, lines, "Alert counts", title, save=save, saveLocation=saveLocation)

def plotOverlap(collectionLocation, plot, save=False, saveLocation=""):

	deviceProps = dict()
	uniqueKeys = set()
	title = "PH:title"

	if plot == "pan-destinationZone": title = "Pan devices overlap with destinationZone"
	elif plot == "pan-sourceZone": title = "Pan devices overlap with sourceZone"
	elif plot == "pan-application": title = "Pan devices overlap with application"
	elif plot == "pan-cat": title = "Pan devices overlap with cat"
	elif plot == "pan-sessionEndReason": title = "Pan devices overlap with sessionEndReason"
	elif plot == "suricata-eventType": title = "Pan devices overlap with eventType"
	elif plot == "suricata-httpStatus": title = "Pan devices overlap with httpStatus"

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if plot == "pan-destinationZone":
			if software != "pan":
				continue
			
			for k in props:
				if k.split("_")[0] == "destinationZone":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "pan-sourceZone":
			if software != "pan":
				continue
			
			for k in props:
				if k.split("_")[0] == "sourceZone":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "pan-application":
			if software != "pan":
				continue
			
			for k in props:
				if k.split("_")[0] == "application":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "pan-cat":
			if software != "pan":
				continue
			
			for k in props:
				if k.split("_")[0] == "cat":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "pan-sessionEndReason":
			if software != "pan":
				continue
			
			for k in props:
				if k.split("_")[0] == "sessionEndReason":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "suricata-eventType":
			if software != "suricata":
				continue
			
			for k in props:
				if k.split("_")[0] == "eventType":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

		elif plot == "suricata-httpStatus":
			if software != "suricata":
				continue
			
			for k in props:
				if k.split("_")[0] == "httpStatus":
					uniqueKeys.add(k)
					if device in deviceProps:
						deviceProps[device].append(props)
					else:
						deviceProps[device] = [props]

	intensity = []
	for device in deviceProps:
		intensityArr = []
		for key in uniqueKeys:
			count = 0
			for props in deviceProps[device]:
				count = count + int(props.get(key, 0))
			
			intensityArr.append(count)
		intensity.append(intensityArr)

	plotHeatmapOverlap(intensity, [x.split("_")[1] for x in uniqueKeys], [x for x in deviceProps], title, save=save, saveLocation=saveLocation)

def plot(collectionLocation, collectionDivLocation, plot, save=False, saveLocation=""):

	if plot == "software-alerts": softwareAlerts(collectionLocation)
	elif plot == "software-alerts-small": softwareAlertsSmall(collectionLocation)
	elif plot == "device-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "suricata-alerts": suricataAlerts(collectionLocation)
	elif plot == "ciscoasa-alerts": ciscoasaAlerts(collectionLocation)
	elif plot == "pan-alerts": panAlerts(collectionLocation)
	elif plot == "suricata-protocol": suricataProtocol(collectionLocation)
	elif plot == "ciscoasa-protocol": ciscoasaProtocol(collectionLocation)
	elif plot == "pan-protocol": panProtocol(collectionLocation)

	elif plot == "pan-destinationZone": panDestinationZone(collectionLocation)
	elif plot == "pan-sourceZone": panSourceZone(collectionLocation)
	elif plot == "pan-application": panApplication(collectionLocation)
	elif plot == "pan-cat": panCat(collectionLocation)
	elif plot == "pan-sessionEndReason": panSessionEndReason(collectionLocation)

	elif plot == "suricata-eventType": suricataEventTypes(collectionLocation)
	elif plot == "suricata-httpStatus": suricataHttpStatus(collectionLocation)

	elif plot == "pie-software-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-suricata-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-ciscoasa-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-pan-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)

	elif plot == "totals-alerts": totalsAlerts(collectionLocation)
	elif plot == "totals-div-matches": totalsDivMatches(collectionDivLocation)
	elif plot == "totals-overlap-div": totalsOverlapDiv(collectionDivLocation)
	elif plot == "timelocks": timelocks(collectionLocation)

	elif plot == "div-overtime": divOvertime(collectionDivLocation)
	elif plot == "div-overtime-ciscoasa-pan": divOvertimeCiscoasaPan(collectionDivLocation)

def totalsOverlapDiv(collectionLocation):
	data = dict()
	for _, intervals, props in getCollectionDivMetaEx(collectionLocation):
		if not intervals:
			continue

		for prop in props:
			data[prop] = data.get(prop, 0) + props[prop]

	def sortedFunc(x, y):
		xS = x.split(",")
		yS = y.split(",")
		if len(xS) < 3:
			return -1
		if len(yS) < 3:
			return 1

		xx = int(xS[-1])
		yy = int(yS[-1])

		return -1 if (xx < yy) else 1

	for prop in sorted(sorted(data.keys(), cmp=sortedFunc)):
		if data[prop] > 0:
			print "%s,%s,%d" % ("-".join(prop.split(",")[:-1]), prop.split(",")[-1], data[prop])

def totalsDivMatches(collectionLocation):
	data = dict()
	for _, props in getCollectionDivMeta(collectionLocation):
		for prop in props:
			data[prop] = data.get(prop, 0) + props[prop]

	for prop in data:
		print prop, "=", data[prop]

def divOvertimeCiscoasaPan(collectionLocation):
	data = dict()
	uniqueProps = set()

	for timestamp, hasIntervals, props in getCollectionDivMetaEx(collectionLocation):
		t = dateutil.parser.parse(timestamp)
		if t not in data: data[t] = dict()
		for prop in props:
			propS = prop.split(",")
			if hasIntervals:
				if propS[0] != "ciscoasa" or propS[1] != "pan":
					continue
				if propS[-1] not in ["1","5","10","30","60","600","1800"]:
					continue
			else:
				if len(propS) == 1 and (propS[0] != "ciscoasa" and propS[0] != "pan"):
					continue
				elif len(propS) > 1:
					continue
			
			uniqueProps.add(prop)
			data[t][prop] = props[prop]

	ax = plt.gca()
	timestamps = sorted(data.keys())
	i = 0

	def sortedFunc(x, y):
		xS = x.split(",")
		yS = y.split(",")
		if len(xS) < 3:
			return -1
		if len(yS) < 3:
			return 1

		xx = int(xS[-1])
		yy = int(yS[-1])

		return -1 if (xx < yy) else 1

	for prop in sorted(uniqueProps, cmp=sortedFunc):
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(prop, 0))
		
		if all(x == 0 for x in line):
			continue

		plt.plot_date(timestamps, line,
			label=prop,
			xdate=True,
			linestyle="solid",
			marker=".",
			color=COLORS["div-lines-ciscoasa-pan"][prop]
		)

		#ax.annotate(prop,
		#	xy=(timestamps[-1], line[-1]),
		#	textcoords="figure fraction",
		#	xytext=(0.9, 0.85-(0.03*i)),
		#	arrowprops={"arrowstyle":"->"},
		#	color=COLORS["div-lines-ciscoasa-pan"][prop]
		#)
		i += 1

	ax = plt.gca()
	ax.set_yscale("symlog",
		linthreshy=100000
	)

	plt.title("Unique src/dst ip:port pairs over time for ciscoasa-pan")
	plt.legend(loc=9, ncol=11)
	plt.show()
	plt.close()
					

def divOvertime(collectionDivLocation):
	data = dict()
	uniqueProps = set()

	for timestamp, props in getCollectionDivMeta(collectionDivLocation):
		t = dateutil.parser.parse(timestamp)
		if t not in data: data[t] = dict()
		for prop in props:
			uniqueProps.add(prop)
			data[t][prop] = props[prop]

	timestamps = sorted(data.keys())
	for prop in uniqueProps:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(prop, 0))
		
		if all(x == 0 for x in line):
			continue

		plt.plot_date(timestamps, line,
			label=prop,
			xdate=True,
			linestyle="solid",
			marker=".",
			color=COLORS["div-lines"][prop]
		)

	ax = plt.gca()
	ax.set_yscale("symlog",
		linthreshy=100,
		linscaley=4
	)

	plt.title("Unique src/dst ip:port pairs over time")
	plt.legend(loc=9, ncol=11)
	plt.show()
	plt.close()

def totalsAlerts(collectionLocation):
	softwares = dict()
	devices = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software not in devices: devices[software] = dict()
		softwares[software] = softwares.get(software, 0) + int(props.get("alerts", 0))
		devices[software][device] = devices[software].get(device, 0) + int(props.get("alerts", 0))

	for software in softwares:
		print "%s,%s" % (software, softwares[software])
	
	for software in devices:
		print "%s:" % software
		for device in devices[software]:
			print "%s,%s" % (device, devices[software][device])

def timelocks(collectionLocation):
	timestamps = set()
	data = dict()

	i = 1
	for timestamp, software, device, _ in getCollectionFiles(collectionLocation):
		t = dateutil.parser.parse(timestamp)
		timestamps.add(t)
		if software not in data: data[software] = dict()
		if device not in data[software]:
			data[software][device] = {"min": t, "max": t, "id": ("%s-%s" % (software, device))}
			i += 1
		else:
			if t < data[software][device]["min"]: data[software][device]["min"] = t
			if t > data[software][device]["max"]: data[software][device]["max"] = t

	for software in data:
		for device in data[software]:
			plt.plot_date(
				[data[software][device]["min"], data[software][device]["max"]],
				[data[software][device]["id"], data[software][device]["id"]],
				xdate=True,
				label=("%s-%s" % (software, device)),
				linestyle="solid",
				marker=".",
				color=COLORS["softwares"][software]
			)

	plt.title("Data start time and end time for each device")
	plt.show()
	plt.close()
				

def ciscoasaAlerts(collectionLocation):
	uniqueDevices = set()
	data = dict()
	
	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "ciscoasa":
			continue

		uniqueDevices.add(device)

		t = dateutil.parser.parse(timestamp)
		data[t] = data.get(t, dict())
		data[t][device] = data[t].get(device, 0) + int(props.get("alerts"))
	
	timestamps = sorted(data.keys())

	for device in uniqueDevices:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(device, 0))

		plt.plot_date(timestamps, line, 
			label=device,
			xdate=True, 
			linestyle="solid",
			marker=".",
			color=COLORS["ciscoasa-devices"][device]
		)

	lastData = []
	for device in uniqueDevices:
		toApp = [device, data[timestamps[-1]].get(device, 0)]
		lastData.append(toApp)

	ax = plt.gca()
	i = 0
	for point in sorted(lastData, key=lambda x: x[1], reverse=True):
		i += 1
		ax.annotate(point[0], 
			xy=(timestamps[-1], point[1]),
			textcoords="figure fraction",
			xytext=(0.90, 0.85-(0.03*i)),
			arrowprops={"arrowstyle":"->"},
			color=COLORS["ciscoasa-devices"][point[0]]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	ax.set_yscale("symlog",
		linthreshy=999,
		linscaley=2,
	)

	plt.title("Ciscoasa device alert counts over time")
	#plt.legend()
	plt.show()
	plt.close()

def suricataProtocol(collectionLocation):
	uniqueProtocols = set()
	data = dict()

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "suricata":
			continue
		
		for prop in props:
			if prop.split("_")[0] == "protocol":
				protocol = prop.split("_")[1]
				uniqueProtocols.add(protocol)
				t = dateutil.parser.parse(timestamp)
				data[t] = data.get(t, dict())
				data[t][protocol] = data[t].get(protocol, 0) + int(props[prop])

	timestamps = sorted(data.keys())

	for protocol in uniqueProtocols:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(protocol, 0))

		plt.plot_date(timestamps, line,
			label=protocol,
			xdate=True,
			linestyle="solid",
			marker=".",
			color=COLORS["protocols"][protocol]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	

	plt.title("Suricata alert counts over time by protocol")
	plt.legend()
	plt.show()
	plt.close()

def ciscoasaProtocol(collectionLocation):
	uniqueProtocols = set()
	data = dict()

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "ciscoasa":
			continue
		
		for prop in props:
			if prop.split("_")[0] == "protocol":
				protocol = prop.split("_")[1]
				uniqueProtocols.add(protocol)
				t = dateutil.parser.parse(timestamp)
				data[t] = data.get(t, dict())
				data[t][protocol] = data[t].get(protocol, 0) + int(props[prop])

	timestamps = sorted(data.keys())

	for protocol in uniqueProtocols:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(protocol, 0))

		plt.plot_date(timestamps, line,
			label=protocol,
			xdate=True,
			linestyle="solid",
			marker=".",
			color=COLORS["protocols"][protocol]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	ax.set_yscale("symlog")
	

	plt.title("Ciscoasa alert counts over time by protocol")
	plt.legend()
	plt.show()
	plt.close()

def panProtocol(collectionLocation):
	uniqueProtocols = set()
	data = dict()

	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		for prop in props:
			if prop.split("_")[0] == "protocol":
				protocol = prop.split("_")[1]
				uniqueProtocols.add(protocol)
				t = dateutil.parser.parse(timestamp)
				data[t] = data.get(t, dict())
				data[t][protocol] = data[t].get(protocol, 0) + int(props[prop])

	timestamps = sorted(data.keys())

	for protocol in uniqueProtocols:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(protocol, 0))

		plt.plot_date(timestamps, line,
			label=protocol,
			xdate=True,
			linestyle="solid",
			marker=".",
			color=COLORS["protocols"][protocol]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	ax.set_yscale("symlog")
	

	plt.title("Pan alert counts over time by protocol")
	plt.legend(loc=9, ncol=10)
	plt.show()
	plt.close()

def suricataAlerts(collectionLocation):
	uniqueDevices = set()
	data = dict()
	
	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "suricata":
			continue

		uniqueDevices.add(device)

		t = dateutil.parser.parse(timestamp)
		data[t] = data.get(t, dict())
		data[t][device] = data[t].get(device, 0) + int(props.get("alerts"))
	
	timestamps = sorted(data.keys())

	for device in uniqueDevices:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(device, 0))

		plt.plot_date(timestamps, line, 
			label=device,
			xdate=True, 
			linestyle="solid",
			marker=".",
			color=COLORS["suricata-devices"][device]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	ax.set_yscale("symlog", linthreshy=10000)
	

	plt.title("Suricata device alert counts over time")
	plt.legend()
	plt.show()
	plt.close()

def panAlerts(collectionLocation):
	uniqueDevices = set()
	data = dict()
	
	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue

		uniqueDevices.add(device)

		t = dateutil.parser.parse(timestamp)
		data[t] = data.get(t, dict())
		data[t][device] = data[t].get(device, 0) + int(props.get("alerts"))
	
	timestamps = sorted(data.keys())

	for device in uniqueDevices:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(device, 0))

		plt.plot_date(timestamps, line, 
			label=device,
			xdate=True, 
			linestyle="solid",
			marker=".",
			color=COLORS["pan-devices"][device]
		)

	lastData = []
	for device in uniqueDevices:
		toApp = [device, data[timestamps[-1]].get(device, 0)]
		lastData.append(toApp)

	ax = plt.gca()
	i = 0
	for point in sorted(lastData, key=lambda x: x[1], reverse=True):
		i += 1
		ax.annotate(point[0], 
			xy=(timestamps[-1], point[1]),
			textcoords="figure fraction",
			xytext=(0.90, 0.85-(0.03*i)),
			arrowprops={"arrowstyle":"->"},
			color=COLORS["pan-devices"][point[0]]
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")
	ax.set_yscale("symlog",
		linthreshy=999,
		linscaley=2,
	)

	plt.title("Pan device alert counts over time")
	#plt.legend()
	plt.show()
	plt.close()

def softwareAlerts(collectionLocation):
	uniqueSoftwares = set()
	data = dict()
	
	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software not in ["suricata", "ciscoasa", "pan"]:
			continue

		uniqueSoftwares.add(software)

		t = dateutil.parser.parse(timestamp)
		data[t] = data.get(t, dict())
		data[t][software] = data[t].get(software, 0) + int(props.get("alerts"))
	
	timestamps = sorted(data.keys())

	for software in uniqueSoftwares:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(software, 0))

		plt.plot_date(timestamps, line, 
			label=software, 
			xdate=True, 
			linestyle="solid", 
			color=COLORS["softwares"][software],
			marker=".",
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")

	plt.title("Software alert counts over time")
	plt.legend()
	plt.show()
	plt.close()

def softwareAlertsSmall(collectionLocation):
	uniqueSoftwares = set()
	data = dict()
	
	for timestamp, software, device, props in getCollectionFiles(collectionLocation):
		if software not in ["bro", "ciscovpn", "mcafee"]:
			continue

		uniqueSoftwares.add(software)

		t = dateutil.parser.parse(timestamp)
		data[t] = data.get(t, dict())
		data[t][software] = data[t].get(software, 0) + int(props.get("alerts"))
	
	timestamps = sorted(data.keys())

	for software in uniqueSoftwares:
		line = list()
		for timestamp in timestamps:
			line.append(data[timestamp].get(software, 0))

		plt.plot_date(timestamps, line, 
			label=software, 
			xdate=True, 
			linestyle="solid", 
			color=COLORS["softwares"][software],
			marker=".",
		)

	## X axis
	plt.xlabel("Timestamps")

	## Y axis
	ax = plt.gca()
	formatter = ticker.StrMethodFormatter('{x:,.0f}')
	ax.yaxis.set_major_formatter(formatter)
	plt.ylabel("Alert counts")

	plt.title("Software alert counts over time")
	plt.legend()
	plt.show()
	plt.close()

def plotOverTime(timestamps, lines, ylabel, title, save=False, saveLocation=""):
	for label in lines:
		plt.plot(timestamps, lines[label], label=label)

	ax = plt.gca()
	formatter = ticker.ScalarFormatter()
	formatter.set_scientific(False)
	ax.yaxis.set_major_formatter(formatter)

	plt.xlabel("Timestamps")
	## Function to get x timestamps ticks from the list of all timestamps
	f = lambda m, n: [i*n//m + n//(2*m) for i in range(m)]
	showIndexes = f(min(len(timestamps), 6), len(timestamps))
	ax.set_xticks([timestamps[x] if (x in showIndexes or x == 0 or x == len(timestamps)) else "" for x in range(len(timestamps))])
	plt.xticks(rotation="vertical")

	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.gcf().set_size_inches(16, 8)

	if save:
		plt.savefig(os.path.join(saveLocation, title))
	else:
		plt.show()

	plt.close()

def plotPie(values, labels, title, save=False, saveLocation=""):
	plt.pie(values, labels=labels, autopct=(lambda x:x))
	plt.title(title)
	plt.gcf().set_size_inches(16, 8)
	if save:
		plt.savefig(os.path.join(saveLocation, title))
	else:
		plt.show()
	plt.close()

def plotHeatmapOverlap(values, xticks, yticks, title, mask=None, save=False, saveLocation=""):
	formatter = ticker.ScalarFormatter()
	formatter.set_scientific(False)
	sns.heatmap(values, xticklabels=xticks, yticklabels=yticks, mask=mask, vmin=0.1, cmap="GnBu", linewidths=1.5, cbar_kws={"format": formatter})

	plt.title(title)
	plt.gcf().set_size_inches(16, 8)
	if save:
		plt.savefig(os.path.join(saveLocation, title))
	else:
		plt.show()
	plt.close()

def panCat(collectionLocation):
	uniqueDevices = set()
	uniqueCat = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_", 1)[0] == "cat":
				k1, k2 = prop.split("_", 1)
				uniqueCat.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for cat in sorted(uniqueCat):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(cat, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values,
		yticklabels=sorted(uniqueCat),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)
	
	plt.title("Pan devices overlap in cat")
	plt.show()
	plt.close()

def panSessionEndReason(collectionLocation):
	uniqueDevices = set()
	uniqueReasons = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_", 1)[0] == "sessionEndReason":
				k1, k2 = prop.split("_", 1)
				uniqueReasons.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for reason in sorted(uniqueReasons):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(reason, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values,
		yticklabels=sorted(uniqueReasons),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)
	
	plt.title("Pan devices overlap in SessionEndReason")
	plt.show()
	plt.close()

def panApplication(collectionLocation):
	uniqueDevices = set()
	uniqueApplications = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_", 1)[0] == "application":
				k1, k2 = prop.split("_", 1)
				uniqueApplications.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for application in sorted(uniqueApplications):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(application, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values,
		yticklabels=sorted(uniqueApplications),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)
	
	plt.title("Pan devices overlap in Application")
	plt.show()
	plt.close()

def panDestinationZone(collectionLocation):
	uniqueDevices = set()
	uniqueZones = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_", 1)[0] == "destinationZone":
				k1, k2 = prop.split("_", 1)
				uniqueZones.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for zone in sorted(uniqueZones):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(zone, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values,
		yticklabels=sorted(uniqueZones),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)
	
	plt.title("Pan devices overlap in DestinationZone")
	plt.show()
	plt.close()

def panSourceZone(collectionLocation):
	uniqueDevices = set()
	uniqueZones = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "pan":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_", 1)[0] == "sourceZone":
				k1, k2 = prop.split("_", 1)
				uniqueZones.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for zone in sorted(uniqueZones):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(zone, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values,
		yticklabels=sorted(uniqueZones),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)
	
	plt.title("Pan devices overlap in SourceZone")
	plt.show()
	plt.close()

def suricataEventTypes(collectionLocation):
	uniqueDevices = set()
	uniqueEventTypes = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "suricata":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_")[0] == "eventType":
				k1, k2 = prop.split("_")
				uniqueEventTypes.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for eventType in sorted(uniqueEventTypes):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(eventType, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values, 
		yticklabels=sorted(uniqueEventTypes),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
	)

	plt.title("Suricata devices overlap in event type")
	plt.show()
	plt.close()

def suricataHttpStatus(collectionLocation):
	uniqueDevices = set()
	uniqueStatus = set()
	data = dict()

	for _, software, device, props in getCollectionFiles(collectionLocation):
		if software != "suricata":
			continue
		
		uniqueDevices.add(device)
		if device not in data: data[device] = dict()
		for prop in props:
			if prop.split("_")[0] == "httpStatus":
				k1, k2 = prop.split("_")
				uniqueStatus.add(k2)
				data[device][k2] = data[device].get(k2, 0) + int(props[prop])

	values = []
	for status in sorted(uniqueStatus):
		toApp = []
		for device in sorted(uniqueDevices):
			value = data[device].get(status, float("nan"))
			toApp.append(value)

		values.append(toApp)

	sns.heatmap(values, 
		yticklabels=sorted(uniqueStatus),
		xticklabels=sorted(uniqueDevices),
		cmap="Reds",
		robust=True,
		annot=True,
		linewidths=.5
	)

	plt.title("Suricata devices overlap in http status")
	plt.show()
	plt.close()