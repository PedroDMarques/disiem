import os
from des_collectionreader import CollectionReader

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
sns.set()

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

def plot(collectionLocation, plot, save=False, saveLocation=""):

	if plot == "software-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "device-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "suricata-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "ciscoasa-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-alerts": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "suricata-protocol": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "ciscoasa-protocol": plotDataOverTime(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-protocol": plotDataOverTime(collectionLocation, plot, save, saveLocation)

	elif plot == "pan-destinationZone": plotOverlap(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-sourceZone": plotOverlap(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-application": plotOverlap(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-cat": plotOverlap(collectionLocation, plot, save, saveLocation)
	elif plot == "pan-sessionEndReason": plotOverlap(collectionLocation, plot, save, saveLocation)

	elif plot == "suricata-eventType": plotOverlap(collectionLocation, plot, save, saveLocation)
	elif plot == "suricata-httpStatus": plotOverlap(collectionLocation, plot, save, saveLocation)

	elif plot == "pie-software-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-suricata-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-ciscoasa-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)
	elif plot == "pie-pan-alerts": plotDataPie(collectionLocation, plot, save, saveLocation)

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