import sys, copy

import tornado.ioloop
import tornado.web
import tornado.httpserver
import updateRecord, textSearch

from conf import scripts_home, public, invalidate
from base64 import b64encode

class ServerResponse():
	def __init__(self):
		self.result = 403
		
	def emit(self):
		return self.__dict__

class Sources(tornado.web.RequestHandler):
	def get(self):
		"""List all Sources in database"""
		res = ServerResponse()

		res.data = db.query(
			"_design/sources/_view/getSources",
			remove=['_rev','rt_']
		)
		if len(res.data) > 0 and res.data[0]:
			res.result = 200
		else:
			del res.data
		
		self.write(res.emit())

	def post(self):
		"""Add a new Source to the database.
		
		Only the server may utilize this method.
		
		required parameters in post:
			_id
			package_name
			package_content
		"""
		
		res = ServerResponse()		
		params = parseRequest(self.request.body)
		
		if params is not None:
			source = ICSource(inflate={'_id' : params['_id']})
			if source.addFile(params['package_name'], params['package_content']):				
				if source.importAssets(params['package_name']):
					res.result = 200
					res.data = source.emit()
				else:
					source.invalidate(
						invalidate['codes']['source_invalid_public_credentials'],
						invalidate['reasons']['source_invalid_public_credentials']
					)
					res.reason = source.invalid
			
		self.write(res.emit())
				
class Source(tornado.web.RequestHandler):
	def initialize(self, source_id):
		self.source_id = source_id
		
	def get(self, source_id):
		"""Returns the specified Source.
		
		required:
			_id
		"""
		res = ServerResponse()
		
		if passesParameterFilter(source_id):
			source = ICSource(_id = source_id)
			
			if not hasattr(source, 'invalid'):
				res.data = source.emit()
				res.result = 200
			else:
				res.reason = source.invalid
		
		self.write(res.emit())
		
class Submissions(tornado.web.RequestHandler):
	def get(self):
		"""Lists all Submissions in the database."""
		
		res = ServerResponse()
		
		res.data = db.query(
			"_design/submissions/_view/getSubmissions",
			remove=['_rev','rt_']
		)
		if len(res.data) > 0 and res.data[0]:
			res.result = 200
		else:
			del res.data
			
		self.write(res.emit())
	
	def post(self):
		"""Add a new Submission to the database.
		
		Only the server may utilize this method.
		
		required parameters in post:
			_id
			package_name
			package_content
		"""
		
		res = ServerResponse()		
		params = parseRequest(self.request.body)

		if params is not None:
			submission = ICSubmission(inflate={'_id' : params['_id']})
			if submission.addFile(params['package_name'], params['package_content']):
				if submission.importAssets(params['package_name']):
					submission.setMimeType(params['mime_type'])
					
					res.result = 200
					res.data = submission.emit()
				else:
					submission.invalidate(
						invalidate['codes']['asset_non_existent'],
						invalidate['reasons']['asset_non_existent']
					)
					res.reason = submission.invalid
		
		self.write(res.emit())
		
class Submission(tornado.web.RequestHandler):
	def initialize(self, submission_id):
		self.submission_id = submission_id

	def get(self, submission_id):
		"""Returns the specified Submission.
		
		required:
			_id
		"""
		res = ServerResponse()
		
		if passesParameterFilter(submission_id):
			submission = ICSubmission(_id = submission_id)
			
			if not hasattr(submission, 'invalid'):
				res.data = submission.emit()
				res.result = 200
			else:
				res.reason = submission.invalid

		self.write(res.emit())

class PublicCredentials(tornado.web.RequestHandler):
	def get(self):
		 """Returns the organization's public information, so users may submit data."""
		 
		 res = ServerResponse()
		 res.result = 200
		 res.data = public_credentials
		 
		 self.write(res.emit())

routes = [
	(r"/sources/", Sources),
	(r"/source/(.*)/", Source, dict(source_id=None)),
	(r"/submissions/", Submissions),
	(r"/submission/(.*)/", Submission, dict(submission_id=None)),
	(r"/public/", PublicCredentials),
        (r"/getSolrIndex", textSearch.solrIndex),
        (r"/createDerivative/(\w+)", updateRecord.createDerivative),
]

api = tornado.web.Application(routes)

if __name__ == "__main__":
	sys.path.insert(0, scripts_home['python'])
	from InformaCamModels.source import Source as ICSource
	from InformaCamModels.submission import Submission as ICSubmission
	from InformaCamUtils.funcs import parseRequest, parseArguments, passesParameterFilter, gzipAsset
	from InformaCamUtils.couch import DB
	
	db = DB()
	public_credentials = copy.deepcopy(public)
	public_credentials['publicKey'] = b64encode(gzipAsset(public['publicKey']))
	for f, form in enumerate(public['forms']):
		public_credentials['forms'][f] = b64encode(gzipAsset(form))
	
	server = tornado.httpserver.HTTPServer(api)
	server.listen(6666)
	
	tornado.ioloop.IOLoop.instance().start()