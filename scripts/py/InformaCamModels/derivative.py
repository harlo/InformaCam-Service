from asset import Asset

def translateFormValue(form_data):
	from conf import form_fields

	if len(form_fields['translate']) > 0:
		
		for key, value in form_data.iteritems():			
			for ff in form_fields['translate']:
				if ff['key'] == str(key):
					form_data[key] = ff['values'][int(value) - 1]

	return form_data

class Derivative(Asset):
	def __init__(self, inflate=None, _id=None):
		super(Derivative, self).__init__(inflate, _id, db="derivatives")