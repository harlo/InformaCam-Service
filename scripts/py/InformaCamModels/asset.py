import time, couchdb, base64

from InformaCamUtils.couch import DB
from InformaCamUtils.funcs import ShellReader
from conf import invalidate

__metaclass__ = type

emit_omits = [
	'db',
	'_rev'
]

rt_ = {
	'source' : 1,
	'submission' : 2
}

class Asset():
	def __init__(self, inflate=None, _id=None):
		self.db = DB()
		
		if _id is None:
			if inflate is not None:
				self.inflate(inflate)

			self.date_admitted = time.time() * 1000		#in milliseconds!	
			
			res = self.db.post(self.emit())
			self._id = res['_id']
			self._rev = res['_rev']
			
		else:
			print "getting by id %s" % _id
			
			asset = self.db.get(_id)
			
			if asset is not None:
				self.inflate(asset)
			else:
				self.invalid = {
					"error_code": invalidate['codes']['asset_non_existent'],
					"reason" : invalidate['reasons']['asset_non_existent']
				}
					
	def makeDir(self, path):
		ShellReader(["mkdir", path])
		
		self.asset_path = path
		self.save()
		
	def addFile(self, file_name, content):
		try:
			content = base64.b64decode(content)
		except TypeError:
			content += "=" * ((4 - len(content) % 4) % 4)
			content = base64.b64decode(content)
			
		file = open("%s/%s" % (self.asset_path, file_name), 'wb+')
		file.write(content)
		file.close()

		return True
		
	def importAssets(self, file_name):
		print "importing asset %s" % file_name
	
	def save(self):
		self.db.put(self._id, self._rev, self.emit())
		
	def invalidate(self, error_code, reason):
		self.invalid = {
			"error_code" : error_code,
			"reason" : reason
		}
		self.save()
		
	def emit(self):
		emit = {}
		for key, value in self.__dict__.iteritems():
			if not key in emit_omits:
				emit[key] = value
			
		return emit
		
	def inflate(self, inflate):
		for key, value in inflate.iteritems():
			setattr(self, key, value)
