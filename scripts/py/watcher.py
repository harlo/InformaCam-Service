import os, sys, time, re

from daemon import runner
from base64 import b64encode

from conf import sync, sync_sleep, assets_root, j3m, scripts_home
from InformaCamUtils.funcs import callApi

def watch():
	"""For each subscribed repository, this class sends new media to our Data API.
	
	"""
	print "running watch..."
	clients = []
	for sync_type in sync:
		if sync_type == "drive":
			from InformaCamData.drive_client import DriveClient	
			clients.append(DriveClient())
		elif sync_type == "globaleaks":
			from InformaCamData.globaleaks_client import GlobaleaksClient
			clients.append(GlobaleaksClient())
	
	for client in clients:
		for asset in client.listAssets(omit_absorbed=True):		
			mime_type = client.getAssetMimeType(asset)		
			if not mime_type in client.mime_types.itervalues():
				continue		
	
			data = {
				'_id': client.getFileNameHash(asset),
				'package_name' : client.getFileName(asset),
				'package_content' : b64encode(client.pullFile(asset)).rstrip("=")
			}
			api_call = None
	
			if mime_type == client.mime_types['zip']:
				# MAYBE THIS IS A LOG, THOUGH?
				api_call = "sources"				
			else:
				api_call = "submissions"
				if data['package_name'][-3 :] != client.mime_type_map[mime_type]:
					data['package_name'] = "%s.%s" % (
						data['package_name'], 
						client.mime_type_map[mime_type]
					)

			if api_call is not None:
				res = callApi(api_call, data=data, post=True)
				print res
				if res['result'] == 200:
					client.absorb(asset)
					client.lockFile(asset)

class Watcher():
	"""The daemon class that pulls new media from subscribed repositories every 10 minutes."""
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path = '/var/run/informacam_watcher.pid'
		self.pidfile_timeout = 5
		
	def run(self):
		while True:
			watch()
			time.sleep(sync_sleep * 60)
			
if __name__ == "__main__":
	print "starting watcher to run at an interval of %d minutes" % sync_sleep
	sys.path.insert(0, scripts_home['python'])

	watcher = Watcher()
	daemon_runner = runner.DaemonRunner(watcher)
	daemon_runner.do_action()
