from asset import Asset

class CellID(Asset):
	def __init__(self, inflate=None, _id=None):
		super(CellID, self).__init__(inflate, _id, db="consolidated")