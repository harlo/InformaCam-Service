import threading

class SearchThreader(threading.Thread):
	def __init__(self):
		print "init"
		
	def run(self):
		print "running"