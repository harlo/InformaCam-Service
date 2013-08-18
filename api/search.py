import re

class Search():
	def __init__(self, params):
		from couch import DB
		self.db = DB(db="derivatives")
		
		q = None
		geo = None
		
		try:
			q = params['keywords']
			del params['keywords']
		except KeyError as e:
			print "no keyworkds specified"
			
		try:
			geo = {
				'latitude' : params['latitude'],
				'longitude' : params['longitude']
			}
			
			del params['latitude']
			del params['longitude']
		except KeyError as e:
			print "no lat/lng specified"
			
		if geo is not None:
			try:
				geo['radius'] = params['radius']
				del params['radius']
			except KeyError as e:
				print "no radius for geo query.  setting default as 5km"
				geo['radius'] = 5
		
		if not any(params):
			params = None
		
		derivatives = []
		if q is not None:	
			derivatives = self.db.lucene_query("_design/textsearch/search_all", q=q, params=params)
		else:
			derivatives = self.db.multiparam_query(params)
			
		if geo is not None:
			geos = self.db.geoquery(geo)
			if len(derivatives) > 0 and derivatives[0]:
				derivatives = list(set(derivatives).intersection(set(geos)))
			else:
				derivatives = geos
		
		if len(derivatives) > 0 and derivatives[0]:
			keys = self.db.query("_design/static/_view/getDerivatives", params={'_ids':derivatives}, include_only=["submission_id"], include_only_as_list=True)
							
			db = DB()
			self.data = db.query("_design/submissions/_view/getSubmissions", params={'_ids':keys})
		else:
			self.data = [False]
			
	def perform(self):
		return self.data