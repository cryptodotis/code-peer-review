#!/usr/bin/python

import time,os

import synonymmapping

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
		
def fixDates(start, end):
	try:
		int(end)
		int(start)
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