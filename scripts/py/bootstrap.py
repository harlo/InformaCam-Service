from conf import form_fields
from InformaCamModels.fti_template import FTITemplate, anno_inner, inner, wrapper, anno_wrapper

def initForms():
	inners = []
	anno_inners = []
	
	for idx in form_fields['fti']:
		inners.append(inner % {'key' : idx})
		anno_inners.append(anno_inner % {'key' : idx})
	
	search_all = (wrapper % "\n".join(inners))
	search_annos = (anno_wrapper % "\n".join(anno_inners))
	
	fti_template = FTITemplate(search_all, search_annos)
	
	for idx in form_fields['fti']:
		fti_template.addSearchField(idx)
	
	print fti_template.emit()

if __name__ == "__main__":
	print "ATTEMPTING BOOTSTRAP"
	
	initForms()