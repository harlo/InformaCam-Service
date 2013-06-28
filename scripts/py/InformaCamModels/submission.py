from asset import Asset, rt_
from conf import assets_root

class Submission(Asset):
	def __init__(self, inflate=None, _id=None):
		if _id is None:
			if inflate is not None:
				inflate['rt_'] = rt_['submission']
			else:
				inflate = {
					'rt_' : rt_['submission']
				}
				
		super(Submission, self).__init__(inflate, _id)
		if hasattr(self, 'asset_path'):
			pass
		else:
			super(Submission, self).makeDir("%ssubmissions/%s" % (assets_root, self._id))
			
	def importAssets(self, file_name):
		# J3MIFY! and handle fail condition...
		
		self.j3m = "%sjson" % file_name[:-3]
		self.file_name = file_name
		self.save()

		return True
