from asset import Asset

def translateFormValue(form_data):
	from conf import form_fields
	from funcs import AsTrueValue

	if len(form_fields['translate']) > 0:
		
		for key, value in form_data.iteritems():
			'''
			for ff in form_fields['binary']:
				if ff['key'] == str(key):
					del form_data['key']
					continue
			'''
					
			for ff in form_fields['translate']:
				if ff['key'] == str(key):
					# TODO: THIS MIGHT BE AN ARRAY!
					form_data[key] = ff['values'][int(value) - 1]
	
	return form_data

class Derivative(Asset):
	def __init__(self, inflate=None, _id=None):
		super(Derivative, self).__init__(inflate, _id, db="derivatives")
		
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