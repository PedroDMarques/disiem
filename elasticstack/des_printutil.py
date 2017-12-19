BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def colorTab(color=WHITE):
	return "\033[1;37;%dm \033[1;37;40m " % (40+color)

def colorText(msg, color=WHITE):
	return "\033[1;%d;40m%s\033[1;%d;40m " % (30+color, msg, 30+WHITE)

def colorLog(t, msg, color=None):
	if not color:
		if t == "info": color = YELLOW
		elif t == "warning" or t == "error" or t == "danger": color = RED
		elif t == "success": color = GREEN
		elif t == "info-2": color = BLUE
		else: color = WHITE

	return colorTab(color) + colorText(msg, color)