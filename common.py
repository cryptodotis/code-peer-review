#!/usr/bin/python

import time,os,urlparse,re, datetime

import synonymmapping

def unixToGitDateFormat(t):
	s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
	return s

def getSynonyms(log, paths):
	log = log.lower()
	for i in range(len(paths)):	paths[i] = paths[i].lower()
	
	keywords = set()
	for k in synonymmapping.map:
		if k in log:
			keywords.add(k)
			for v in synonymmapping.map[k]: keywords.add(v)
		for p in paths:
			if k in p:
				keywords.add(k)
				for v in synonymmapping.map[k]: keywords.add(v)
	
	return keywords
	
def getBasePath(paths):
	trunks = [p for p in paths if "/trunk" in p]
	branches = [p for p in paths if "/branches" in p]
	tags = [p for p in paths if "/tags" in p]
	odd = [p for p in paths if p not in trunks and p not in branches and p not in tags]
	if ((1 if len(trunks) > 0 else 0) + (1 if len(branches) > 0 else 0) + \
		(1 if len(tags) > 0 else 0) + (1 if len(odd) > 0 else 0)) > 1:
		ret = []
		if len(trunks) > 0: ret.append(os.path.commonprefix(trunks))
		if len(branches) > 0: ret.append(os.path.commonprefix(branches))
		if len(tags) > 0: ret.append(os.path.commonprefix(tags))
		if len(odd) > 0: ret.append(os.path.commonprefix(odd))
		return ret
	else:
		return os.path.dirname(os.path.commonprefix(paths))

re_gitsvn = re.compile('git-svn-id: \w+://.+ \w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}')		
def cleanUpCommitMessage(msg):
	msg = re.sub(re_gitsvn, '', msg)
	return msg.strip()

def urlToFolder(url):
	scheme, netloc, path, parameters, query, fragment = urlparse.urlparse(url)
	folder = netloc + path
	folder = folder.replace('/', '-')
	return folder

def fixDates(start, end):
	try:
		end = int(end)
		start = int(start)
	except ValueError:
		print "Invalid Start or End Date"
		exit
		
	if end == 0 and start < 0:
		end = time.time()
		start = end + int(start)
	elif end < start:
		tmp = end
		end = start
		start = tmp
	return start, end
