from asset import Asset

class BTDevice(Asset):
	def __init__(self, inflate=None, _id=None):
		super(BTDevice, self).__init__(inflate, _id, db="consolidated")