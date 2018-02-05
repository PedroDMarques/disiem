import os
from des_collectionreader import CollectionReader

import numpy as np
import matplotlib.pyplot as plt
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

def plotDataOverTime(collectionLocation, plot):
	data = dict()
	uniqueKeys = set()
	title = "PH:title"

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

	plotOverTime(timestamps, lines, "Alert counts", title)

def plot(collectionLocation, plot):

	if plot == "software-alerts": plotDataOverTime(collectionLocation, plot)
	elif plot == "device-alerts": plotDataOverTime(collectionLocation, plot)
	elif plot == "suricata-alerts": plotDataOverTime(collectionLocation, plot)
	elif plot == "ciscoasa-alerts": plotDataOverTime(collectionLocation, plot)
	elif plot == "pan-alerts": plotDataOverTime(collectionLocation, plot)
	elif plot == "suricata-protocol": plotDataOverTime(collectionLocation, plot)
	elif plot == "ciscoasa-protocol": plotDataOverTime(collectionLocation, plot)
	elif plot == "pan-protocol": plotDataOverTime(collectionLocation, plot)

def plotOverTime(timestamps, lines, ylabel, title):
	for label in lines:
		plt.plot(timestamps, lines[label], label=label)

	plt.xlabel("Timestamps")
	plt.ylabel(ylabel)
	plt.title(title)
	plt.legend()
	plt.show()
	plt.close()

def plotHeatmapOverlap(values, xticks, yticks, title):
	sns.heatmap(values, xticklabels=xticks, yticklabels=yticks)
	plt.title(title)
	plt.show()
	plt.close()