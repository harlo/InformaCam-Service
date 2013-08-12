import json, copy, md5, time, os
from conf import file_salt, scripts_home, mime_types, mime_type_map

__metaclass__ = type

class InformaCamDataClient():
	def __init__(self):
		self.mime_types = copy.deepcopy(mime_types)
		self.mime_type_map = copy.deepcopy(mime_type_map)
		
	def loadConf(self, path):
		"""Loads any credentials for the repository.
		
		"""
		conf = open(path, 'rb')
		j = json.loads(conf.read())
		conf.close()
		
		return j
		
	def listAssets(self, omit_absorbed=False):
		"""Lists any assets available in the repository.
		
		arguments:
			omit_absorbed (boolean)
				flag to ignore files that the server has already processed.
		"""
		print "listing assets"
		
	def pullFile(self, file):
		"""Downloads the actual file onto disk.
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "pulling file %s" % file
		
	def lockFile(self, file):
		"""Makes the media on the repository unavailable to the public, if possible.
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "locking file %s" % file
		
	def getFile(self, file_id):
		"""Gets file's metadata from the repository.
		
		arguments:
			file_id (string)
				usually an id for the file
		"""
		print "getting file %s" % file_id
		
	def absorb(self, file):
		"""Marks file as absorbed by the server.  Subsequent pulls to the repository may omit files that have been absorbed.
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "absorbing file %s" % file
		
	def isAbsorbed(self, file):
		"""Determines whether a file has been absorbed by the server.
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "finding out if file is absorbed %s" % file
		
	def getAssetMimeType(self, file_id):
		"""Gets the mime type of a file.
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "getting asset mime type %s" % file_id
		
	def validateMediaObject(self, file_id, returnType=False):
		"""Checks a file to see if it indeed is image or mkv video.
		
		arguments
			file_id (string or object)
		"""
		print "validating media object %s" % file_id
		
	def mapMimeTypeToExtension(self, mime_type):
		print "mapping mime type to extension"
		
	def getFileName(self, file):
		"""Gets the file name of a file (not to be confused with its id).
		
		arguments:
			file (string or object)
				usually an id for the file
		"""
		print "getting a file name (label, not hashed Id)"
		
		
	def getFileNameHash(self, name_base):
		"""Creates a unique hash for the file.  Can (should!) be used to generate the file's id in the database.
		
		arguments:
			name_base (string)
				usually the file's name
		"""	
		m = md5.new()
		m.update(name_base)
		m.update(file_salt)
		m.update(repr(time.time()))
		
		return m.hexdigest()