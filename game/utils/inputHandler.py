# From https://gist.github.com/jasonrdsouza/1901709#gistcomment-2734411
def getchar():
	# Returns a single character from standard input
	import os, signal
	ch = ''
	if os.name == 'nt': # how it works on windows
		import msvcrt
		ch = msvcrt.getch()
	else:
		import tty, termios, sys
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	if ord(ch) == 3:
		pass # Handle ctrl+C - This is equivalent to ignoring SIGINT
	return ch
