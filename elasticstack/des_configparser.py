import ConfigParser

OPTIONS = {
	"data_location": {
		"section": "LOCATION",
		"format": "String",
		"description": "data_location description",
		"default": "../data",
		"parse_load": (lambda x: x),
		"parse_save": (lambda x: x),
	},

	"save_location": {
		"section": "LOCATION",
		"format": "String",
		"description": "save_location description",
		"default": "../data_parsed",
		"parse_load": (lambda x: x),
		"parse_save": (lambda x: x),
	},

	"elasticsearch_index": {
		"section": "LOCATION",
		"format": "String",
		"description": "elasticsearch_index description",
		"default": "disiem_test",
		"parse_load": (lambda x: x),
		"parse_save": (lambda x: x),
	},

	"ignore_software": {
		"section": "FILTERS",
		"format": "List of strings separated by commas",
		"description": "ignore_software description",
		"default": "",
		"parse_load": (lambda x: x.split(",")),
		"parse_save": (lambda x: ",".join(x) if type(x) == list else x),
	},

	"ignore_device": {
		"section": "FILTERS",
		"format": "List of strings separated by commas",
		"description": "ignore_device description",
		"default": "",
		"parse_load": (lambda x: x.split(",")),
		"parse_save": (lambda x: ",".join(x) if type(x) == list else x),
	},

	"ignore_file_name": {
		"section": "FILTERS",
		"format": "List of strings separated by commas",
		"description": "ignore_file_name description",
		"default": "_SUCCESS",
		"parse_load": (lambda x: x.split(",")),
		"parse_save": (lambda x: ",".join(x) if type(x) == list else x),
	},

	"ignore_file_extension": {
		"section": "FILTERS",
		"format": "List of strings separated by commas",
		"description": "ignore_file_extension description",
		"default": "gz,zip",
		"parse_load": (lambda x: x.split(",")),
		"parse_save": (lambda x: ",".join(x) if type(x) == list else x),
	},

	"min_data_file_size": {
		"section": "FILTERS",
		"format": "Integer value or empty string",
		"description": "min_data_file_size description",
		"default": "",
		"parse_load": (lambda x: int(x) if x else False),
		"parse_save": (lambda x: x),
	},

	"max_data_file_size": {
		"section": "FILTERS",
		"format": "Integer value or empty string",
		"description": "max_data_file_size description",
		"default": "",
		"parse_load": (lambda x: int(x) if x else False),
		"parse_save": (lambda x: x),
	},

	"data_file_includes_timestamp": {
		"section": "FILTERS",
		"format": "Date in string in the format '2017-04-16T10:00:00.000000+00:00'",
		"description": "data_file_includes_timestamp description",
		"default": "",
		"parse_load": (lambda x: x),
		"parse_save": (lambda x: x),
	},

	"time_chunks": {
		"section": "PARSING",
		"format": "Integer in minutes",
		"description": "time_chunks description",
		"default": "60",
		"parse_load": (lambda x: int(x) / 2 * 60),
		"parse_save": (lambda x: x),
	},
}

OPTIONS_ORDER = [
	"data_location", "save_location", "elasticsearch_index", "ignore_software",
	"ignore_device", "ignore_file_name", "ignore_file_extension",
	"min_data_file_size", "max_data_file_size", "data_file_includes_timestamp",
	"time_chunks",
]

def getDefaultOptions():
	"""
	Returns a dictionary with all of the options mapping to their default values

	Returns:
		{dict} A dictionary with all of the options mapping to their default values
	"""
	options = {}
	for name in OPTIONS:
		options[name] = OPTIONS[name]["default"]
	
	return options

def writeConfigFile(path="config.cfg", default=False):
	"""
	Write a configuration file prompting the user for each value

	Parameters:
		{str} [path="config.cfg"] The path to write the config file in
		{bool} [default=False] If set to True will not prompt the user for values and will use all default values
	"""
	options = {}
	if default:
		options = getDefaultOptions()
	else:
		for name in OPTIONS_ORDER:
			option = OPTIONS[name]
			s = "%s\n%s.\n%s. [%s] " % (name, option["format"], option["description"], option["default"])
			value = raw_input(s)
			value = option["parse_save"](value) if value else option["default"]
			options[name] = value

	parser = ConfigParser.RawConfigParser()
	for name in OPTIONS_ORDER:
		option = OPTIONS[name]
		if not parser.has_section(option["section"]):
			parser.add_section(option["section"])

		parser.set(option["section"], name, options[name])

	parser.write(open(path, "w"))

class Configuration(object):
	def __init__(self, path=None, default=False):
		"""
		Creates a new Configuration object

		Parameters:
			{bool} [default=False] If set will initialize the Configuration will all the default values
			{str} [path=None] If set will read the values from the specified path. Note that this only works if not set alongside "default"
		"""
		if default:
			self.options = getDefaultOptions()
		elif path:
			self.read(path)
		else:
			self.options = {}

	def read(self, path="config.cfg", parser=None):
		"""
		Read the configuration file at the specified path and override any current options
		Any option that isn't found in the configuration file is set to it's default value

		Parameters:
			{str} path The path to the configuration file to read
			{ConfigParser.RawConfigParser} parser If set will use the parser given instead of reading from a file
		"""
		self.options = {}
		if not parser:
			parser = ConfigParser.RawConfigParser()
			parser.read(path)

		for name in OPTIONS:
			option = OPTIONS[name]
			value = option["default"]
			
			if parser.has_section(option["section"]):
				if parser.has_option(option["section"], name):
					value = parser.get(option["section"], name)

			self.options[name] = value

	def getOption(self, name):
		"""
		Get an option by name

		Parameters:
			{str} name The name of the option to get

		Returns:
			{*} The value of the option
		"""
		return OPTIONS[name]["parse_load"](self.options[name])

	def setOption(self, name, value):
		"""
		Set the value of an option by name

		Parameters:
			{str} name The name of the option to set
			{str} value The value to set
		"""
		self.options[name] = OPTIONS[name]["parse_save"](value)

	def __str__(self):
		s = ""
		writenSections = []
		for name in OPTIONS_ORDER:
			option = OPTIONS[name]
			if option["section"] not in writenSections:
				s += "\n[%s]\n" % option["section"]
				writenSections.append(option["section"])

			s += "%s = %s\n" % (name, self.options[name])

		return s

	def __repr__(self):
		return self.options.__repr__()