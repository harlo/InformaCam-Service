import sys, os, re
from bs4 import BeautifulSoup as BS

class ScrapeResult():
	def __init__(self, params):
		self.entries = []
		for param in params:
			setattr(self, "%s_index" % param, 0)

class Wigle():	
	def __init__(self):
		if not self.isLoggedIn():
			self.logIn()
			
		if not self.parseWigleCookie():
			self.logIn()

	def isLoggedIn(self):
		try:
			with open(wigle_conf['cookie_jar']) :
				return True
		except IOError:
			return False
		
	def logIn(self):
		print "logging in..."
		login_data = {
			'credential_0' : wigle_conf['username'],
			'credential_1' : wigle_conf['password']
		}
		call = ExternalApiThreader(
			url="%s%s" % (wigle_conf['base_url'], wigle_conf['login_url']), 
			data=login_data, 
			post=True,
			cookiejar=wigle_conf['cookie_jar']
		)
		call.start()
		call.join()
				
	def logOut(self):
		print "logging out..."
		if self.isLoggedIn():
			call = ExternalApiThreader(
				url="%s%s" % (wigle_conf['base_url'], wigle_conf['logout_url'])
			)
			call.start()
			call.join()
		
			os.remove(wigle_conf['cookie_jar'])

	def parseWigleCookie(self):
		if self.isLoggedIn():
			pattern = 'auth\t'
			
			for line in open(wigle_conf['cookie_jar'], 'r'):
				if line.find('.wigle.net') >= 0 and line.find(pattern) >= 0:
					cookie = re.compile('%s.+' % pattern).search(line).group()
					if len(cookie) > 0:
						self.cookie = cookie.replace(pattern,'')
						break
					
			if hasattr(self, 'cookie'):
				return True
			
		print "Uh-oh, could not parse cookie"	
		return False			
	
	def unUnicode(self, data):
		return AsTrueValue(unicode.join(u'\n', map(unicode, data)))
	
	def soupScrape(self, html, params):
		result = ScrapeResult(params)
				
		rows = BS(html).findAll('tr', {'class' : 'search'})
		headers = rows[0].findAll('td')
		
		idx = 0
		for header in headers: 			
			for p in params:
				if re.match(p, self.unUnicode(header.findAll(text=True))):
					setattr(result, "%s_index" % p, idx)
					
			idx += 1	

		for row in rows[1:]:
			entry = {}
			for p in params:
				idx = getattr(result, "%s_index" % p)
				entry[p] = self.unUnicode(row.findAll('td')[idx].findAll(text=True))
				
			result.entries.append(entry)
		
		return result
	
	def queryByBSSID(self, bssid):
		call = ExternalApiThreader(
			url = "%s%s" % (wigle_conf['base_url'], wigle_conf['query_url']),
			data = {
				'netid':bssid,
				'Query':'Query'
			},
			post = True,
			send_cookie = "auth=%s" % self.cookie
		)
		call.start()
		call.join()
		
		return self.soupScrape(call.output, ['latitude','longitude'])
	
if __name__ == "__main__":
	test_bssid = "0A:2C:EF:3D:25:1B"
	sys.path.insert(0, "/Users/LvH/ORG/witness/API/API_V2/conf/")
	sys.path.insert(0, "/Users/LvH/ORG/witness/API/API_V2/scripts/py/InformaCamUtils/")

	from conf import wigle as wigle_conf
	from funcs import ExternalApiThreader, AsTrueValue
	wigle = Wigle()
	locations = wigle.queryByBSSID(test_bssid)
	
	print locations.entries
		

