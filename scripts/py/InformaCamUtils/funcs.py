import sys, subprocess, os, cStringIO, pycurl, re, json
from conf import api

def callApi(url, data=None, post=False):
	url = "http://localhost:%d/%s/" % (api['port'], url)
	
	buf = cStringIO.StringIO()
	d = []
	dataString = None
	
	c = pycurl.Curl()
	
	c.setopt(c.VERBOSE, False)
	c.setopt(c.WRITEFUNCTION, buf.write)
	
	if data is not None:	# data is a dict
		for key, value in data.iteritems():
			d.append("%s=%s" % (key, value))
		dataString = "&".join(d)
		
		if not post:
			url = "%s?%s" % (url, dataString)
		else:
			c.setopt(c.POSTFIELDS, dataString)
		
	print "CALLING API ON %s" % url	
	c.setopt(c.URL, url)
	c.perform()
	
	res = buf.getvalue()
	buf.close()
	
	return json.loads(str(res))
		
def saveRawFile(destination, content):
	file = open(destination, 'w+')
	file.write(content)
	file.close()
	return True

def passesParameterFilter(req):	
	# looking for pipes
	match = re.search(r'\s*\|\s*.+', req)
	if match:
		print "found a pipe:\n%s" % match.group()
		return False

	# looking for two periods and slashes "\..\"
	match = re.search(r'\.\./', req)
	if match:
		print "found a file inclusion attempt:\n%s" % match.group()
		return False

	# looking for XSS using broken element tags (i.e. <svg/onload=alert(1)>
	match = re.search(r'<\s*\w+/\s*.+=.*\s*>', req)
	if match:
		print "found an XSS attempt using broken element tag:\n%s" % match.group()	
		return False

	return True

def parseRequest(request_string):
	try:
		if passesParameterFilter(request_string):
			return json.loads(request_string)
		else:
			return None
	except ValueError as e:
		print e

	params = dict()
	for kvp in request_string.split("&"):
		k = kvp.split("=")[0]
		v = kvp.split("=")[1]
		if passesParameterFilter(k) and passesParameterFilter(v):
			params[k] = AsTrueValue(v)	# this might catch on arrays; please check!

	return params

def parseArguments(arguments):
	params = dict()

	for key in arguments:
		if not passesParameterFilter(key):
			return None

		for k in arguments[key]: 
			params[key] = []
			if k[0] is "[" and k[-1] is "]":				
				for value_ in str(k[1:-1]).split("],["):
					arr = []
					for value in value_.split(","):
						if passesParameterFilter(value):
							arr.append(AsTrueValue(value))

					params[key].append(arr)
			else:
				for value in k.split(","):
					if passesParameterFilter(value):
						params[key].append(AsTrueValue(value))

	print "%s transformed to %s" % (arguments, params)
	return params

def AsTrueValue(str_value):
	if str_value.startswith("[") and str_value.endswith("]"):
		vals = []
		for v_ in str(str_value[1:-1]).split(","):
			vals.append(AsTrueValue(v_))

		return vals
	if str_value == "0":
		return int(0)
	if str_value == "true":
		return True
	if str_value == "false":
		return False
	try:
		if int(str_value):
			return int(str_value)
		elif float(str_value):
			return float(str_value)
	except ValueError:
		return str_value

def GetTrueValue(str_value):
	str_value = str(str_value)
	if str_value[0] is "[" and str_value[1] is "]":
		return 'list'
	if str_value == "0":
		return 'int'
	if str_value == "true" or str_value == "false":
		return 'bool'
	try:
		if int(str_value):
			return 'int'
		elif float(str_value):
			return 'float'
	except ValueError as e:
		print "GET TRUE VALUE ERROR: %s so i returned str" % e
		return 'str'
		
def ShellReader(cmd, omitNewLine = True):
	print "CMD: %s" % cmd

	data_read = []
	ex = subprocess.Popen(
		cmd,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		close_fds=True
	)
	(stdout, stdin) = (ex.stdout, ex.stdin)
	data = stdout.readline()
	while data:
		print data

		if omitNewLine is True and (data.find("\n") or data.find("\r")):
			data_read.append(data[:-1])
		else:	
			data_read.append(data)

		data = stdout.readline()

	stdout.close()
	stdin.close()

	return data_read