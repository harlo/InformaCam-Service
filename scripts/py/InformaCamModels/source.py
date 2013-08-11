from asset import Asset, rt_
from conf import gnupg_home, assets_root, invalidate
from InformaCamUtils.funcs import ShellReader

import gnupg, json

class Source(Asset):
	def __init__(self, inflate=None, _id=None):
		if _id is None:
			if inflate is not None:
				inflate['rt_'] = rt_['source']
			else:
				inflate = {
					'rt_': rt_['source']
				}
				
		super(Source, self).__init__(inflate, _id)
		
		if hasattr(self, 'invalid'):
			return
		
		if hasattr(self, 'asset_path'):
			pass
		else:
			super(Source, self).makeDir("%ssources/%s" % (assets_root, self._id))
	
	def importAssets(self, asset_name):

		ShellReader([
			"unzip", 
			"%s/%s" % (self.asset_path, asset_name), 
			"-d", 
			self.asset_path
		])
		self.importKey("%s/publicKey" % self.asset_path)
		self.baseImage = "%s/baseImage" % self.asset_path
		
		c = open("%s/credentials" % self.asset_path, 'rb')
		credentials = json.loads(c.read())
		c.close()
		
		try:
			self.alias = credentials['alias']
		except:
			pass
			
		try:
			self.email = credentials['email']
		except:
			pass

		self.save()
		return True
	
	def importKey(self, path_to_key):
		gpg = gnupg.GPG(gnupghome=gnupg_home)
		
		key = open(path_to_key)
		import_result = gpg.import_keys(key.read())
		key.close()
				
		self.fingerprint = import_result.results[0]['fingerprint']

		if self.fingerprint is not None:
			self.save()
			return True
		else:
			self.invalidate(
				invalidate['codes']['source_invalid_pgp_key'],
				invalidate['reasons']['source_invalid_pgp_key']
			)
			return False
	
	def getBaseImage(self):
		return self.baseImage