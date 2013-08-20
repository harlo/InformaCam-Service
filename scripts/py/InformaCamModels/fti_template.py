from asset import Asset, emit_omits
from conf import form_fields
from couch import DB

import copy

inner = """if(\"%(key)s\" in annotation.content) {
	ret.add(annotation.content.%(key)s);
}
"""

anno_inner = """if(\"%(key)s\" in annotation.content) {
	var ret_ = new Document();
	ret_.add(annotation.content.%(key)s);
	ret_.add(k, {\"type\":\"int\", \"field\":\"anno_index\", \"store\":\"yes\"});
	ret.push(ret_);
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

anno_wrapper = """function(doc) {
	if(!(\"annotations\" in doc)) {
		return;
	}
	
	var ret = new Array();
	for(var k=0; k<doc.annotations.length; k++) {
		var annotation = doc.annotations[k];
		%s
	}
	
	return ret;
}
"""

class FTITemplate(Asset):
	def __init__(self, search_all=None, search_annos=None):
		self._id = "_design/textsearch"
		self.db = DB(db="derivatives")
		self.emit_omits = copy.deepcopy(emit_omits)
		
		asset = self.db.get(self._id)
		if asset is None:
			self._rev = self.db.post(self.emit())['_rev']
			
			self.fulltext = {}
			try:
				self.addSearchField('search_all', index=search_all)
			except:
				pass
				
			try:
				self.addSearchField('search_annos', index=search_annos)
			except:
				pass
		else:
			self.inflate(asset)
			
	def addSearchField(self, field, index=None):
		if index is None:
			index = wrapper % (inner % {'key' : field})
			field = "by_%s" % field
			
		self.fulltext[field] = {
			'index' : index.replace("\n","").replace("\t","")
		}
		
		self.save()