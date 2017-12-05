BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
CYAN = 6
WHITE = 7

def colorTab(color=WHITE):
	"""
	Get a string that will print out a colored tab. One single monospace cell with a background color
	@param {Number} [color=WHITE] The background color of the tab to return. Defaults to white
	@returns {String}
	"""
	return "\033[1;37;%dm \033[1;37;40m " % (40+color)

def colorText(msg, color=WHITE):
	"""
	Get a string that will print out a specified message in a specified color
	@param {String} msg The message to color
	@param {Number} [color=WHITE] The color to use for the message
	@returns {String} 
	"""
	return "\033[1;%d;40m%s\033[1;%d;40m " % (30+color, msg, 30+WHITE)