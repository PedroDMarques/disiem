import ConfigParser

class ConfigError(Exception):
	"""Error raised when the configuration scripts encounters an error"""
	pass

class Option(object):
	def __init__(self, name, section, type, description, default):
		"""
		Parameters:
			{str} name The name of the option
			{str} section The section in which the option is found
			{str} type The type of the option ["list", "int", "date"]
			{str} description A description of the option
			{str} default The default value of the option
		"""
		self.name = name
		self.section = section
		self.type = type
		self.description = description
		self.default = default

	def getWritePrompt(self):
		"""
		Returns a string to output to the console, prompting the user to input a value for the option
		
		Returns:
			{String} A string to output to the console

		"""
		t = ""
		if self.type == "list":
			t = "List of words separated by a comma or empty string"
		elif self.type == "int":
			t = "Integer value or empty string"
		elif self.type == "date":
			t = "Date in the format '2017-04-16T10:00:00.000000+00:00'"

		return "%s\n%s. %s [%s]" % (self.name, self.description, t, self.default)

	def __str__(self):
		return "Option (%s -> %s)" % (self.section, self.name)

	def __repr__(self):
		return self.__str__()

options = [
	Option("ignore_software", "FILTERING", "list", "A list of software types to ignore from the data files", ""),
	Option("ignore_device", "FILTERING", "list", "A list of device names to ignore from the data files", ""),
	Option("ignore_file_name", "FILTERING", "list", "A list of file names to ignore from the data files", "_SUCCESS"),
	Option("ignore_file_ext", "FILTERING", "list", "A list of file extensions to ignore from the data files", "gz,zip"),
	Option("min_file_size", "FILTERING", "int", "The minimum size of data files to accept, in bytes", ""),
	Option("max_file_size", "FILTERING", "int", "The maximum size of data files to accept, in bytes", ""),
	Option("included_timestamp", "FILTERING", "date", "A timestamp that must be included in the data file", ""),
]

optionsDict = dict()
for option in options:
	optionsDict[option.name] = option

def writeConfig(fileName="config.cfg", defaultMode=False):
	"""
	Prompts the user all of the options to write in the configuration file, and saves the new configuration in the file system

	Parameters:
		{str} [fileName="config.cfg"] The path of the file to save the configurations under
		{bool} [defaultMode=False] If set to true the configuration file will be created with default values and without prompting the user
	"""
	if defaultMode:
		writingConfig = getDefaultConfig()
	else:
		writingConfig = ConfigParser.RawConfigParser()

		for option in options:
			if not writingConfig.has_section(option.section):
				writingConfig.add_section(option.section)
			
			value = raw_input("\n%s: " % (option.getWritePrompt()))
			writingConfig.set(option.section, option.name, value if value else option.default)

	writingConfig.write(open(fileName, "w"))

def getDefaultConfig():
	"""
	Returns a config object with all the default values

	Returns:
		{CconfigParser.RawConfigParser} A config object with all the default values
	"""
	config = ConfigParser.RawConfigParser()
	for option in options:
		if not config.has_section(option.section):
			config.add_section(option.section)

		config.set(option.section, option.name, option.default)
	
	return config

def parseValue(value, type):
	"""
	Parses the given value in accordance to the type of value the option should contain

	Parameters:
		{*} value A value to parse

	Returns:
		{*} The parsed value in accordance to the type of the option
	"""
	if type == "list":
		return value.split(",")
	elif type == "int":
		try:
			return int(value)
		except:
			return False
	
	return value

class Config(object):
	def __init__(self, path, defaultMode=False):
		"""
		Constructs a Config object

		Parameters:
			{str} path The path of the configuration file that should be read
			{bool} [defaultMode=False] If True will use a default config object with default values instead of reading from a file
		"""
		if defaultMode:
			self.config = getDefaultConfig()
		else:
			self.config = ConfigParser.RawConfigParser()
			self.config.read(path)

		if not self.config.sections:
			raise ConfigError("No configuration file found, or no content in configuration file.")

		for option in options:
			if not self.config.has_option(option.section, option.name):
				raise ConfigError("Configuration file was read but does not contain option %s in section %s" % (option.name, option.section))

	def getOption(self, option, overrideValue=""):
		"""
		Returns an option from the configuration, correctly parsed. If overrideValue is specified then returns that same value, also parsed

		Parameters:
			{str} option The name of the option to return
			{str} [overrideValue=""] If specified, this value will be parsed and returns instead of the value in the configuration

		Returns:
			{*} The value of the configuration option
		"""
		option = optionsDict[option]
		
		if overrideValue:
			return parseValue(overrideValue, option.type)
	
		return parseValue(self.config.get(option.section, option.name), option.type)

	def __str__(self):
		toRet = ""
		for section in self.config.sections():
			toRet += "[%s]\n" % (section)
			
			for option in self.config.options(section):
				value = self.config.get(section, option)
				toRet += "%s = %s\n" % (option, value)

			toRet += "\n"
		
		return toRet

	def __repr__(self):
		return self.__str__()