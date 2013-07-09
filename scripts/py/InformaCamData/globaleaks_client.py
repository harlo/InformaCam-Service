import magic, os, json, sys, re
from informacam_data_client import InformaCamDataClient
from conf import globaleaks, scripts_home

sys.path.insert(0, "%sInformaCamUtils" % scripts_home['python'])
from funcs import ShellReader

class GlobaleaksClient(InformaCamDataClient):
  def __init__(self):
		super(GlobaleaksClient, self).__init__()
		
		os.chdir("%sInformaCamData" % scripts_home['python'])
		try:
			f = open(globaleaks['absorbed_log'], 'rb')			
			self.absorbedByInformaCam = json.loads(f.read())
			f.close()
		except:
			self.absorbedByInformaCam = {
				globaleaks['absorbed_flag'] : []
			}	
	
	def sshToHost(self, function, extras=None):
		args = [
			"host=%s" % globaleaks['host'],
			"user=%s" % globaleaks['user'],
			"key_filename=%s" % globaleaks['identity_file'],
			"asset_root=%s" % globaleaks['asset_root']
		]
		
		if extras is not None:
			args = args + extras
			
		print args
		
		return ShellReader([
			"fab",
			"-f",
			os.path.join(os.getcwd(), "ssh_helper.py"),
			"%s:%s" % (function, ",".join(args))
		])
	
	def getAssetMimeType(self, fileId):
		super(GlobaleaksClient, self).getAssetMimeType(fileId)
		
		self.sshToHost('pullFile', extras=[
			"file=%s" % fileId,
			"asset_dump=%s@%s:/home/%s" % (
				globaleaks['user'], 
				globaleaks['host'], 
				globaleaks['user']
			),
			"local_dump=%s" % os.getcwd()
		])
		
		m = magic.Magic(flags=magic.MAGIC_MIME_TYPE)
		mime_type = m.id_filename(os.path.join(os.getcwd(), fileId))
		m.close()
		
		return mime_type
		
		return None
	
	def mapMimeTypeToExtension(self, mime_type):
		super(GlobaleaksClient, self).mapMimeTypeToExtension(mime_type)
		
		return self.mime_type_map[mime_type]
		
	def getFile(self, fileId):
		super(GlobaleaksClient, self).getFile(fileId)
		
		# does nothing, really
		return fileId
		
	def pullFile(self, file):
		super(GlobaleaksClient, self).pullFile(file)
		# already pulled.
		
		file = os.path.join(os.getcwd(), file)
		f = open(file, 'rb')
		content = f.read()
		f.close()
		
		return content
		
	def lockFile(self, file):
		super(GlobaleaksClient, self).lockFile(file)
		
		file = os.path.join(os.getcwd(), file)
		ShellReader(['rm', file])
		
	def listAssets(self, omit_absorbed=False):
		super(GlobaleaksClient, self).listAssets(omit_absorbed)
		
		assets = []
		sentinel = "[%s] out: " % globaleaks['host']
		
		for line in self.sshToHost('listAssets'):
			l_match = re.search(re.escape(sentinel), line)
			if l_match is not None:
				files = line[len(sentinel) :].split("  ")
				for file in files:
					file = file.replace("\r","")
					if omit_absorbed and self.isAbsorbed(file):
						continue
						
					assets.append(file)

		return assets
		
	def isAbsorbed(self, file):
		super(GlobaleaksClient, self).isAbsorbed(file)
		
		# if we've seen the name before...
		f = os.path.basename(file)
		if f in self.absorbedByInformaCam[globaleaks['absorbed_flag']]:
		 	return True
		
		return False

	def absorb(self, file):
		super(GlobaleaksClient, self).absorb(file)

		self.absorbedByInformaCam[globaleaks['absorbed_flag']].append(
			os.path.basename(file)
		)
		
		f = open(globaleaks['absorbed_log'], 'wb+')
		f.write(json.dumps(self.absorbedByInformaCam))
		f.close()
		
	def getFileName(self, file):
		super(GlobaleaksClient, self).getFileName(file)

		return file
	
	def getFileNameHash(self, file):
		return super(GlobaleaksClient, self).getFileNameHash(file)
