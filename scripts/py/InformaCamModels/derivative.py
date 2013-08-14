import threading, time, os, json, sys

from asset import Asset, rt_, emit_omits
from bssid import BSSID
from cell_id import CellID
from bt_device import BTDevice
from conf import context_codes, invalidate, scripts_home, validity_buffer, form_fields

sys.path.insert(0, "%sInformaCamUtils" % scripts_home['python'])
from couch import DB
from funcs import isWithinRange, isNearby, AsTrueValue, callApi

class DerivativeThreader(threading.Thread):
	def __init__(self, submission):
		threading.Thread.__init__(self)
		self.submission = submission
		self.num_tries = 0
		self.max_tries = 10000
		self.success = False
		
	def run(self):
		while not self.j3mAvailable() and self.num_tries <= self.max_tries:
			self.num_tries += 1
			time.sleep(5)
			
		if self.success:
			self.derivative = Derivative(
				inflate={
					'submission_id' : self.submission._id
				}
			)
	
	def j3mAvailable(self):
		try:
			with open(os.path.join(self.submission.asset_path, self.submission.j3m)):
				self.success = True
		except IOError: pass
		return self.success

class Derivative(Asset):
	def __init__(self, inflate=None, _id=None):
		
		super(Derivative, self).__init__(
			inflate=inflate,
			_id=_id,
			db="derivatives",
			extra_omits=['submission','source','j3m']
		)
		
		if not hasattr(self, 'submission_id'):
			self.invalidate(
				invalidate['codes']['submission_undefined'],
				invalidate['reasons']['submission_undefined']
			)
			return
		
		from submission import Submission
		self.submission = Submission(_id=self.submission_id)
		j3m = open(
			os.path.join(self.submission.asset_path, self.submission.j3m), 'r'
		).read()
		
		try:
			self.j3m = json.loads(j3m)
		except:
			self.submission.invalidate(
				invalidate['codes']['submission_invalid_j3m'],
				invalidate['reasons']['submission_invalid_j3m']
			)
			
			self.invalidate(
				invalidate['codes']['submission_invalid_j3m'],
				invalidate['reasons']['submission_invalid_j3m']
			)
			return
		
		from source import Source	
		if _id is None:
			fingerprint = None
			try:
				fingerprint = self.j3m['intent']['pgpKeyFingerprint'].lower()
			except KeyError as e:
				print "NO FINGERPRINT???"
				self.source = Source(inflate={
					'invalid': {
						'error_code' : invalidate['codes']['source_missing_pgp_key'],
						'reason' : invalidate['reasons']['source_missing_pgp_key']
					}
				})
				
			if fingerprint is not None:
				source = self.submission.db.query(
					'_design/sources/_view/getSourceByFingerprint', 
					params={
						'fingerprint' : fingerprint
					}
				)[0]
			
				if source:
					self.source = Source(_id=source['_id'])
				else:
					# we didn't have the pgp key.  
					# so init a new source and set an invalid flag about that.
				
					inflate = {
						'fingerprint' : fingerprint
					}
				
					## TODO: ACTUALLY THIS IS CASE-SENSITIVE!  MUST BE UPPERCASE!
					self.source = Source(inflate=inflate)
					self.source.invalidate(
						invalidate['codes']['source_missing_pgp_key'],
						invalidate['reasons']['source_missing_pgp_key']
					)
			
			
			setattr(self, 'source_id', self.source._id)
			self.save()
			
			self.parseLocationEntries()
			self.parseAnnotationEntries()
		else:
			self.source = Source(_id=self.source_id)
			
	def parseLocationEntries(self):
		print "parsing locations, bssids and cell tower ids; mac addresses (BT)"
		
		capture_min = self.j3m['genealogy']['dateCreated']
		capture_max = capture_min + self.j3m['data']['exif']['duration']
		
		self.known_locations = []
		known_mac_addresses = []
		known_bssids = []
		known_cell_ids = []
		
		for entry in self.j3m['data']['sensorCapture']:
			try:
				known_bssids.extend(self.parseBSSIDs(
					entry['sensorPlayback']['visibleWifiNetworks'], 
					entry['timestamp']
				))
			except KeyError as e: 
				pass
				
			try:
				known_cell_ids.extend(self.parseCellIDs(
					entry['sensorPlayback']['cellTowerId'],
					entry['timestamp']
				))
			except KeyError as e:
				pass
				
			try:
				known_mac_addresses.extend(self.parseMACs(
					entry['sensorPlayback']['bluetoothDeviceAddress'],
					entry['timestamp']
				))
			except KeyError as e:
				pass
		
		if len(self.known_locations) > 0:
			known_locations_ = []
			for known_location in self.known_locations:
				if known_location not in known_locations_:
					known_locations_.append(known_location)
					
			setattr(self, 'known_locations', known_locations_)
			self.save()
		
		if len(known_mac_addresses) > 0:
			setattr(self, 'known_mac_addresses', list(set(known_mac_addresses)))
			self.save()
			
		if len(known_bssids) > 0:
			setattr(self, 'known_bssids', list(set(known_bssids)))
			self.save()
			
		if len(known_cell_ids) > 0:
			setattr(self, 'known_cell_ids', list(set(known_cell_ids)))
			self.save()
		
	def parseAnnotationEntries(self):
		print "parsing annotation entries"
		annotations = []
		
		try:
			if 'userAppendedData' in self.j3m['data']:
				pass
			else:
				return
		except KeyError as e:
			return
			
		for entry in self.j3m['data']['userAppendedData']:
			try:
				for f, form_data in enumerate(entry['associatedForms']):
					annotation = None					
					try:
						annotation = {
							'content' : self.translateFormValue(form_data['answerData']),
							'addedBy' : self.source._id,
							'dateAdded' : entry['timestamp']
						}
					except:
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
						print "no region bounds for annotation: %s" %e
						pass
					
					if annotation is not None:
						print annotation	
						annotations.append(annotation)
			except:
				continue		
		
		if len(annotations) > 0:
			setattr(self, 'annotations', annotations)		
			self.save()
		
	def setDescription(self, description):
		"""Set derivative description.
		
		arguments:
		* description (str)
		"""
		
		setattr(self, 'description', description)
		self.save()
		
	def setAlias(self, alias):
		"""Set derivative alias.
		
		arguments:
		* alias (str)
		"""
		
		setattr(self, 'alias', alias)
		self.save()
		
	def setTier(self, tier):
		"""Set derivative tier.
		
		arguments:
		* tier (str)
		"""
		
		setattr(self, 'tier', tier)
		self.save()
		
	def setStatus(self, status):
		"""Set derivative status.
		
		arguments:
		* status (str)
		"""
		
		setattr(self, 'status', status)
		self.save()
		
	def addCustom(self, custom_key, custom_value):
		"""add custom field and corresponding value to derivative
		
		arguments:
		* custom_key (str)
		* custom_value (dict)
		"""
		
		if not hasattr(self, 'custom'):
			setattr(self, 'custom', {})
			
		self.custom[custom_key] = custom_value
		self.save()
	
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
	
	def translateFormValue(self, form_data):
		if len(form_fields['translate']) > 0:
			for key, value in form_data.iteritems():
				for ff in form_fields['translate']:
					if ff['key'] == str(key):
						# TODO: THIS MIGHT BE AN ARRAY!
						form_data[key] = ff['values'][int(value) - 1]
	
		return form_data
		
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
						location['coorboration'].append(self.source._id)
						location['coorboration'] = list(set(location['coorboration']))
					except KeyError as e:
						location['coorboration'] = [self.source._id]
						
					break
			
			if add_new_location:
				location_object.location.append(new_location)
			
		location_object.save()
		
		del new_location['reportedBy']
		del new_location['dateReported']
		return new_location
		
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
			
			if cell_id.cellId not in found_cell_ids:
				found_cell_ids.append(cell_id.cellId)
							
			parsed_location = self.parseLocationObject(cell_id, timestamp)
			if parsed_location not in self.known_locations:
				self.known_locations.append(parsed_location)
				
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
			
			if bssid.bssid not in found_bssids:
				found_bssids.append(bssid.bssid)
							
			parsed_location = self.parseLocationObject(bssid, timestamp)
			if parsed_location not in self.known_locations:
				self.known_locations.append(parsed_location)
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
			
			if mac.MAC not in found_macs:
				found_macs.append(mac.MAC)
							
			parsed_location = self.parseLocationObject(mac, timestamp)
			if parsed_location not in self.known_locations:
				self.known_locations.append(parsed_location)
		return found_macs