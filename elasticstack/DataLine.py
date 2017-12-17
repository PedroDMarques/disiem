import json

class DataLine(object):
	def __init__(self, line, conf, software, device):
		self.line = line
		self.origProps = json.loads(line)
		self.props = dict()

		self.props["des_software_type"] = software
		self.props["des_device_name"] = device

		if conf["transfer_fields"]:
			for field in conf["transfer_fields"]:
				self.props[field] = self.origProps[field]

		elif conf["ignore_fields"]:
			for field in self.origProps:
				if field not in conf["ignore_fields"]:
					self.props[field] = self.origProps[field]

		for field in conf["parse_fields"]["fields"]:
			value = None
			key = conf["parse_fields"]["fields"][field]
			if key:
				if type(key) is list:
					for subKey in key:
						if subKey in self.origProps:
							value = self.origProps[subKey]
							break

				else:
					if key in self.origProps:
						value = self.origProps[key]

			if value and field in conf["parse_fields"]["parse"]:
				value = conf["parse_fields"]["parse"][field](value)

			self.props[field] = value

		for field in conf["scripted_fields"]:
			self.props[field] = conf["scripted_fields"][field](self.props)

	def getProps(self):
		return self.props