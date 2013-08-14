from asset import Asset, emit_omits
from conf import form_fields
from couch import DB

import copy

inner = """if(\"%(key)s\" in annotation.content) {
	ret.add(annotation.content.%(key)s);
}
"""

wrapper = """function(doc) {
	if(!(\"annotations\" in doc)) {
		return;
	}

	var ret = new Document();
	for(var k=0; k<doc.annotations.length; k++) {
		var annotation = doc.annotations[k];
		%s
	}
	
	return ret;	

}"""

class FTITemplate(Asset):
	def __init__(self, search_all):
		self._id = "_design/textsearch"
		self.db = DB(db="derivatives")
		self.emit_omits = copy.deepcopy(emit_omits)
		
		self._rev = self.db.post(self.emit())['_rev']
		print self.emit()
		
		self.fulltext = {}
		self.addSearchField('search_all', index=search_all)
		
	def addSearchField(self, field, index=None):
		if index is None:
			index = wrapper % (inner % {'key' : field})
			field = "by_%s" % field
			
		self.fulltext[field] = {
			'index' : index.replace("\n","").replace("\t","")
		}
		
		self.save()