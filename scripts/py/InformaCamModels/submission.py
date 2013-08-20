from asset import Asset, rt_
from derivative import DerivativeThreader, DerivativeSearch, Derivative
from conf import assets_root, j3m, scripts_home
import os, sys

class SubmissionSearch():
	def __init__(self, submission, params):
		if not hasattr(submission, 'derivative'):
			return [False]
		
		self.submission = submission	
		self.params = None
		
		try:
			self.q = params['keywords']
			del params['keywords']
		except KeyError as e:
			print "no keywords specified"
			
		if any(params):
			self.params = params
			print self.params
			
		if hasattr(self, 'q') or self.params is not None:
			self.perform()
			
	def perform(self):
		from couch import DB
		self.db = DB("derivatives")
		
		if hasattr(self, 'q'):
			annotations = self.db.anno_query("_design/textsearch/search_annos", q=self.q, _id=self.submission._id)
			
			if annotations[0]:
				self.annotations = annotations

class Submission(Asset):
	def __init__(self, inflate=None, _id=None):
		if _id is None:
			if inflate is not None:
				inflate['rt_'] = rt_['submission']
			else:
				inflate = {
					'rt_' : rt_['submission']
				}
				
		super(Submission, self).__init__(inflate, _id, extra_omits=['derivative', 'refined_search'])
		
		if hasattr(self, 'invalid'):
			return
		
		if hasattr(self, 'asset_path'):
			pass
		else:
			super(Submission, self).makeDir("%ssubmissions/%s" % (assets_root, self._id))
			
		derivative_id = DerivativeSearch({'submissionID':self._id}).derivatives
		print derivative_id
		
		if derivative_id[0]:
			self.derivative = Derivative(_id=derivative_id[0], submission=self)
			
	def setMimeType(self, mime_type):
		setattr(self, 'mime_type', mime_type)
		self.save()
			
	def importAssets(self, file_name):
		self.file_name = file_name
		self.j3m = "%sjson" % self.file_name[:-3]
		self.save()
		
		sys.path.insert(0, "%sInformaCamUtils" % scripts_home['python'])
		from funcs import ShellThreader
				
		j3m_thread = ShellThreader([
			"java", "-cp", j3m['classpath'],
			"framework.MediaProcessor", "%s/%s" % (self.asset_path, self.file_name),
			"%s/" % self.asset_path, "-d"
		], op_dir=j3m['root'])
		j3m_thread.start()
		
		derivative_thread = DerivativeThreader(self)
		derivative_thread.start()
				
		return True
		
	def search(self, params):
		return SubmissionSearch(self, params)	
