from asset import Asset

class BSSID(Asset):
	def __init__(self, inflate=None, _id=None):
		super(BSSID, self).__init__(inflate, _id, db="consolidated")