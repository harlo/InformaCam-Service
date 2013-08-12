import sys, os, threading, json, time

from asset import Asset, rt_, emit_omits
from bssid import BSSID
from cell_id import CellID
from bt_device import BTDevice
from conf import context_codes, invalidate, scripts_home, validity_buffer

sys.path.insert(0, "%sInformaCamUtils" % scripts_home['python'])
from couch import DB
from funcs import isWithinRange, isNearby, AsTrueValue, callApi

class ContextThreader(threading.Thread):
	def __init__(self, submission):
		threading.Thread.__init__(self)
		self.submission = submission
		self.num_tries = 0
		self.max_tries = 100000
		self.success = False
		
	def run(self):
		while not self.j3mAvailable() and self.num_tries <= self.max_tries:
			self.num_tries += 1
			time.sleep(5)
		
		if self.success:
			self.context = Context(inflate={
				'submission_id' : self.submission._id
			})
		
	def j3mAvailable(self):
		try:
			with open(os.path.join(self.submission.asset_path, self.submission.j3m)):
				self.success = True
		except IOError: pass
		return self.success

class Context(Asset):
	def __init__(self, inflate=None, _id=None):
		if _id is None:
			if inflate is not None:
				inflate['rt_'] = rt_['context']
			else:
				inflate = {
					'rt_' : rt_['context']
				}
			
		super(Context, self).__init__(
			inflate, 
			_id, 
			extra_omits=['submission','source','derivative','j3m']
		)
		
		if not hasattr(self, 'submission_id'):
			return
			
		from submission import Submission
		self.submission = Submission(_id=self.submission_id)
		j3m = open(
			os.path.join(self.submission.asset_path, self.submission.j3m), 'r'
		).read()
		
		try:	
			self.j3m = json.loads(j3m)
		except:
			# submission j3m is corrupted or missing
			self.submission.invalidate(
				invaltidate['codes']['submission_invalid_j3m'],
				invalidate['reasons']['submission_invalid_j3m']
			)
			self.submission.save()
			return

		from source import Source
		from derivative import Derivative
		if _id is None:
			source = self.db.query(
				'_design/sources/_view/getSourceByFingerprint', 
				params={
					'fingerprint' : self.j3m['intent']['pgpKeyFingerprint']
				}
			)[0]
			
			if source:
				self.source = Source(_id=source['_id'])
			else:
				# we didn't have the pgp key.  
				# so init a new source and set an invalid flag about that.
				
				inflate = {
					'fingerprint' : self.j3m['intent']['pgpKeyFingerprint'],
				}
				
				self.source = Source(inflate=inflate)
				self.source.invalidate(
					invalidate['codes']['source_missing_pgp_key'],
					invalidate['reasons']['source_missing_pgp_key']
				)
				
			setattr(self, 'source_id', self.source._id)
			
			self.derivative = Derivative(inflate=self.parseDerivativeEntries())
			setattr(self, 'derivative_id', self.derivative._id)
			
			self.parseLocationEntries()
			self.save()
		else:
			self.source = Source(_id=self.source_id)
			self.derivative = Derivative(_id=self.derivative_id)
			
	def parseDerivativeEntries(self):
		keywords = []
		annotations = []
		
		try:
			kw = open(os.path.join(self.submission.asset_path, "key_words_%s" % self.submission.j3m))
			keywords = json.loads(kw.read())['keywords']
			kw.close()
			
		except: pass
				
		from derivative import translateFormValue
		for entry in self.j3m['data']['userAppendedData']:
			try:
				for f, form_data in enumerate(entry['associatedForms']):	
					annotation = None	
					print entry
								
					try:
						annotation = {
							'content' : translateFormValue(form_data['answerData']),
							'addedBy' : self.source._id,
							'dateAdded' : entry['timestamp']
						}
					except:
						continue
						
					if annotation is None:
						continue
						
					try:
						annotation['index'] = entry['index']
					except KeyError as e:
						print "no index for annotation: %s" % e
						pass
						
					try:
						annotation['regionBounds'] = entry['regionBounds']
						
						del annotation['regionBounds']['displayWidth']
						del annotation['regionBounds']['displayHeight']
						del annotation['regionBounds']['displayTop']
						del annotation['regionBounds']['displayLeft']
						
						if annotation['regionBounds']['startTime'] == -1:
							del annotation['regionBounds']['startTime']
							
						if annotation['regionBounds']['endTime'] == -1:
							del annotation['regionBounds']['endTime']
							
					except KeyError as e:
						print "no region bounds for annotation: %s" % e
						pass
						
					
					annotations.append(annotation)
			except:
				continue
			
		return {
			'keywords' : keywords,
			'annotations' : annotations
		}		
	
	def parseLocationEntries(self):
		capture_min = self.j3m['genealogy']['dateCreated']
		capture_max = capture_min + self.j3m['data']['exif']['duration']
		
		print "parsing locations, bssids and cell tower ids; mac addresses (BT)"
		self.known_locations = []
		self.known_mac_addresses = []
		
		for entry in self.j3m['data']['sensorCapture']:
			try:
				self.known_locations.extend(self.parseBSSIDs(
					entry['sensorPlayback']['visibleWifiNetworks'], 
					entry['timestamp']
				))
			except KeyError as e: 
				pass
				
			try:
				self.known_locations.extend(self.parseCellIDs(
					entry['sensorPlayback']['cellTowerId'],
					entry['timestamp']
				))
			except KeyError as e:
				pass
				
			try:
				self.known_mac_addresses.extend(self.parseMACs(
					entry['sensorPlayback']['bluetoothDeviceAddress'],
					entry['timestamp']
				))
			except KeyError as e:
				pass
		
		if len(self.known_locations) == 0:
			del self.known_locations
		else:
			self.known_locations = list(set(self.known_locations))
			
		if len(self.known_mac_addresses) == 0:
			del self.known_mac_addresses
		else:
			self.known_mac_addresses = list(set(self.known_mac_addresses))
			
	def getClosestLocation(self, timestamp):
		validity_range = [
			timestamp - validity_buffer['location'], 
			timestamp + validity_buffer['location']
		]
		
		for entry in self.j3m['data']['sensorCapture']:
			try:
				coords = AsTrueValue(entry['sensorPlayback']['gps_coords'])
				if coords != [0.0, 0.0] and coords != ['0.0','0.0']:
					if isWithinRange(validity_range, timestamp):
						return {
							'latitude' : coords[0],
							'longitude' : coords[1]
						}

			except KeyError as e:
				#print "OOPS: %s" % e
				continue
			
		return None
		
	def parseLocationObject(self, location_object, timestamp):
		new_location = self.getClosestLocation(timestamp)
		if new_location is not None:
			new_location['dateReported'] = time.time() * 1000
			new_location['reportedBy'] = self.source._id
			
			add_new_location = True
		
			if not hasattr(location_object, 'location'):
				setattr(location_object, 'location', [])
								
			# cycle through locations to see if they need updating:
			# is this location relevant to our j3m (within 1 km)?
			# if yes, then we don't have to add it, just update.
			for location in location_object.location:
				if isNearby(new_location, location, 1):
					add_new_location = False
					location['dateLastSeen'] = timestamp
					location['lastSeenBy'] = self.source._id
					
					try:
						if self.submission._id not in location['coorboration']:
							location['coorboration'].append(self.source._id)
					except KeyError as e:
						location['coorboration'] = [self.source._id]
						
					break
			
			if add_new_location:
				location_object.location.append(new_location)
			
		location_object.save()
		return location_object
		
	def parseCellIDs(self, cell_info, timestamp):
		cell_info_list = cell_info
		
		if type(cell_info) != list:
			cell_info_list = []
			cell_info_list.append(cell_info)
			
		consolidated = DB(db="consolidated")
		found_cell_ids = []
				
		for cell_info in cell_info_list:			
			if type(cell_info) != int:
				cell_info = int(cell_info)
				
			inflate = consolidated.query(
				"_design/locations/_view/getByCellID",
				params={
					'cellId' : AsTrueValue(cell_info)
				}
			)[0]
			
			if not inflate:
				inflate = {
					'cellId' : AsTrueValue(cell_info)
				}
				cell_id = CellID(inflate=inflate)
			else:
				cell_id = CellID(_id=inflate['_id'])
			
			found_cell_ids.append(self.parseLocationObject(cell_id, timestamp)._id)
				
		return found_cell_ids
	
	def parseBSSIDs(self, network_info, timestamp):
		network_info_list = network_info
		
		if type(network_info) != list:
			network_info_list = []
			network_info_list.append(network_info)
		
		consolidated = DB(db="consolidated")
		found_bssids = []
			
		for network_info in network_info_list:
			inflate = consolidated.query(
				"_design/locations/_view/getByBSSID", 
				params={
					'bssid' : network_info['bssid']
				}
			)[0]
			
			if not inflate:
				# create a new entry
				inflate = {
					'bssid' : network_info['bssid']
				}
			
				bssid = BSSID(inflate=inflate)
			else:
				bssid = BSSID(_id=inflate['_id'])				
			
			found_bssids.append(self.parseLocationObject(bssid, timestamp)._id)			
		return found_bssids
		
	def parseMACs(self, bt_info, timestamp):
		bt_info_list = bt_info
		
		if type(bt_info) != list:
			bt_info_list = []
			bt_info_list.append(bt_info)
			
		consolidated = DB(db="consolidated")
		found_macs = []
		
		for bt_info in bt_info_list:
			inflate = consolidated.query(
				"_design/locations/_view/getByMACAddress",
				params = {
					'MAC' : bt_info
				}
			)[0]
			
			if not inflate:
				inflate = {
					'MAC' : bt_info
				}
				mac = BTDevice(inflate=inflate)
			else:
				mac = BTDevice(_id=inflate['_id'])
				
			found_macs.append(self.parseLocationObject(mac, timestamp)._id)
		return found_macs