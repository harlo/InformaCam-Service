import urllib, cStringIO, pycurl, subprocess, couchdb, hashlib, funcs
import simplejson as json
from funcs import GetTrueValue, makeBoundingBox
from conf import couch

class Wrapper():
	def __init__(self, view, db=None):
		if db is None:
			db = couch['db']
			
		self.buf = cStringIO.StringIO()
		url = "%s@localhost:5984/%s/%s" % (couch['login'], db, view)
		print url
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, url)
		curl.setopt(pycurl.WRITEFUNCTION, self.buf.write)
		self.curl = curl
		
	def setMethod(self, method):
		self.curl.setopt(pycurl.CUSTOMREQUEST, method)
		
	def perform(self):
		self.curl.perform()
		b_string = self.buf.getvalue()
		self.buf.flush()
		self.buf.close()
		
		return json.loads(b_string)
		
class DB():
	def __init__(self, db=None):
		if db is None:
			self.db_tag = couch['db']
		else:
			self.db_tag = db
			
		server = couchdb.Server("http://%s@localhost:5984" % couch['login'])
		self.db = server[self.db_tag]
		
	def removeKeysFromObject(self, obj, remove):
		for rm in remove:
			try:
				del obj[rm]
			except:
				continue
			
		return obj
		
	def applySort(self, sort):
		if sort == 1:
			return "&limit=10"

	def consolidate(self, parent, children, remove):
		if type(parent) is list:
			count = 0
			for value in parent:
				if type(value) is str:
					for child in children:
						if value == child['_id']:
							if remove is not None:
								child = self.removeKeysFromObject(child, remove)
								
							parent[count] = child
				else:
					self.consolidate(value, children, remove)
					
				count += 1
				
		elif type(parent) is dict:
			
			for key, value in parent.iteritems():
				#print "%s: %s (%s)" % (key, value, type(value))
				for child in children:
					if value == child['_id']:
						if remove is not None:
							child = self.removeKeysFromObject(child, remove)
							
						parent[key] = child
						break

				parent[key] = self.consolidate(value, children, remove)				
		else:
			for child in children:
				print child
				
				if parent == child['_id']:
					if remove is not None:
						child = self.removeKeysFromObject(child, remove)
					
					return child
		
		if remove is not None:
			parent = self.removeKeysFromObject(parent, remove)
						
		return parent
		
	def geoquery(self, geo):
		bbox = str(makeBoundingBox(geo['latitude'], geo['longitude'], geo['radius']))[1:-1].replace(" ","")
		view = "_design/geosearch/_spatial/points?bbox=%s" % bbox
		
		query = Wrapper(view, db=self.db_tag)
		result = []
		
		try:
			for row in query.perform()['rows']:
				try:
					result.append(row['id'])
				except KeyError as e:
					print e
					continue
					
			if len(result) == 0:
				result.append(False)
					
		except KeyError as e:
			print e
			pass
			
		if len(result) == 0:
				result.append(False)
		
		return result
		
	def lucene_query(self, view, q=None, params=None):
		view = "%s?q=" % view
		
		if q is not None:
			view += q
		
		if params is not None:
			if q is not None:
				view += " AND "
				
			vals = []
			for k, v in params.iteritems():
				vals.append("%s:%s" % (k,v))
				
			if len(vals) > 1:
				view += " AND ".join(vals)
			else:
				view += vals[0]
		
		print view
		query = Wrapper(view, db="_fti/local/%s" % self.db_tag)
		result = query.perform()
		
		results = []
		if type(result) == list:
			for rows in result:
				try:
					for row in rows['rows']:
						results.append(row['id'])
				except TypeError as e:
					print e
					continue
		else:
			try:
				for row in result['rows']:
					results.append(row['id'])
			except TypeError as e:
				print e
				pass

			
		if len(results) == 0:
			results.append(False)

		return list(set(results))
		
	def query(self, view, params = None, remove = None, include_only = None, include_only_as_list=False, sort=None):
		# BTW params go in reverse alpha
		if remove is not None:
			remove.append('child_of')
		else:
			remove = ['child_of']
			
		view += "?include_docs=true"
		if params is not None:
			vals = []
			for k, v in params.iteritems():
				if type(v) is str or type(v) is unicode:
					vals.append(urllib.quote("\"%s\"" % v))
				elif type(v) is int:
					vals.append(str(v))
				elif type(v) is bool:
					vals.append(str(v))
				elif type(v) is list:
					for v_ in v:
						if type(v_) is str or type(v_) is unicode:
							vals.append(urllib.quote("\"%s\"" % v_))
						else:
							vals.append(v_)
				else:
					vals.append(v)
			
			if len(vals) > 1:
				view += "&keys=%s%s%s" % (urllib.quote("["), ",".join(vals), urllib.quote("]"))
			else:
				view += "&key=%s" % vals[0]
		
		if sort is not None:
			view += self.applySort(sort)
		
		query = Wrapper(view, db=self.db_tag)
		result = []
		docs = []
		
		try:
			for row in query.perform()['rows']:
				row['value'] = self.removeKeysFromObject(row['value'], remove)
					
				try:
					if type(row['value']) is not bool and len(row['value'].keys()) == 1 and row['value'].keys()[0] == "_id":
						row['doc']['child_of'] = row['key']
						docs.append(row['doc'])
					else:
						result.append(row['value'])
				except KeyError as e:
					print e
					pass
				except AttributeError as e:
					print e
					pass

			if len(result) == 0:
				result.append(False)
			else:
				if include_only is not None:
					remove = list(set(result[0].keys()) - set(include_only))
					
				for res in result:
					res = self.consolidate(res, docs, remove)
					
				if include_only_as_list and len(include_only) == 1:
					result_ = []
					for res in result:
						result_.append(res[include_only[0]])
					result = result_
					
		except KeyError as e:
			result.append(False)
			
		return result
		
	def mapQuery(self, view, params = None, remove = None):
		# BTW params go in reverse alpha
		if remove is not None:
			remove.append('child_of')
		else:
			remove = ['child_of']
			
		if params is not None:
			vals = []
			for k, v in params.iteritems():
				if type(v) is str or type(v) is unicode:
					vals.append(urllib.quote("\"%s\"" % v))
				elif type(v) is int:
					vals.append(str(v))
				elif type(v) is bool:
					vals.append(str(v))
				elif type(v) is list:
					for v_ in v:
						if type(v_) is str or type(v_) is unicode:
							vals.append(urllib.quote("\"%s\"" % v_))
						else:
							vals.append(str(v_))
				else:
					vals.append(v)
			
			if len(vals) > 1:
				view += "?key=%s%s%s" % (urllib.quote("["), urllib.quote(",").join(vals), urllib.quote("]"))
			else:
				view += "?key=%s" % vals[0]
				
		query = Wrapper(view, self.db_tag)
		result = []
		
		try:
			for row in query.perform()['rows']:
				print row['value']
				result.append(row['value'])
		except KeyError as e:
			result.append(False)
			
		return result
		
	def get(self, _id, remove = None, include_only = None):
		try:
			doc = self.db[_id]
			
			if remove is not None:
				doc = self.removeKeysFromObject(doc, remove)
			
			return doc
		except:
			return None
		
	def post(self, params):
		result = {}
		result['_id'], result['_rev'] = self.db.save(params)
		return result
		
	def put(self, _id, _rev, params):
		doc = self.db[_id]
		for k, v in params.iteritems():			
			if not "." in k:
				root_element = k
				target = {}
				target[root_element] = v
			else:
				target = ""
				paths = k.split(".")
				root_element = paths[0]
				depth = 0
				
				for p in paths:
					target += ("{\"%s\":" % p)
					
					if depth == len(paths) - 1:
						if GetTrueValue(v) is not 'str':
							target += v
						else:							
							target += "\"%s\"" % v
						
					depth += 1
				
				for p in paths:
					target += "}"
				
				target = json.loads(target)
				
			try:
				if type(doc[root_element]) is dict:
					doc[root_element].update(target[root_element])					
				else:
					doc[root_element] = target[root_element]
			
			except KeyError as e:
				doc[root_element] = target[root_element]
					
		self.db[_id] = doc
		
	def delete(self, id_, rev_):
		print "deleting"