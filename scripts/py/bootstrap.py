from conf import form_fields
from InformaCamModels.fti_template import FTITemplate, inner, wrapper

if __name__ == "__main__":
	print "ATTEMPTING BOOTSTRAP"
	
	inners = []
	for idx in form_fields['fti']:
		inners.append(inner % {'key' : idx})
	
	search_all = (wrapper % "\n".join(inners))
	fti_template = FTITemplate(search_all)
	
	for idx in form_fields['fti']:
		fti_template.addSearchField(idx)
	
	print fti_template.emit()