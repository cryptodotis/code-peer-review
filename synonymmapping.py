#/usr/bin/python

import MySQLdb
from common import *
from database import DB

map = None

class KeywordType:
	STANDARD = 1
	#standard keywords can appear in a commit message, filename/path, or the diffed code.  
	APICALL = 2
	#api keywords can appear in a commit message or diffed code, and represent an API call to a library
	# the individual tag does not apply, only the parent tag
	MAPPING = 3
	#mapping keywords will not appear anywhere in the log, diff, or pathname, but are used to apply tags and apply a parent tag

def getMap():
	global map
	if map == None:
		conn = DB.getConn()
		c = conn.cursor()

		c.execute("SELECT * FROM " + DB.keyword._table)
		rows = c.fetchall()

		map = {}

		for r in rows:
			if not r[DB.keyword.keyword] in map:
				map[r[DB.keyword.keyword]] = MicroMock(type=1, implies=[])
			if r[DB.keyword.parent]:
				if not r[DB.keyword.parent] in map:
					map[r[DB.keyword.parent]] = MicroMock(type=1, implies=[])

		   		map[r[DB.keyword.keyword]].implies.append(r[DB.keyword.parent])

		c.execute("SELECT tagname FROM " + DB.repo._table)
		rows = c.fetchall()
		for r in rows:
			if not 'project-' + r[0] in map:
				map['project-' + r[0]] = MicroMock(type=1, implies=[])
    
    	return map

def getTags(commit):
	log = commit.message.lower()
	paths = []
	for i in range(len(commit.files)): paths.append(commit.files[i].lower())

	keywords = set()
	for k in getMap():
		kregex = re.compile('(?<=[^a-zA-Z])' + k + '(?![a-zA-Z])') #positive lookbehind, tag, negative lookahead.  
		# k is not surrounded by alpha characters.  
		# Matches tor, +tor, (tor), tor(, but not gotor, hitorhi, or tortor
		
		if kregex.search(log):
			keywords.add(k)
			for v in map[k].implies: keywords.add(v)
		for p in paths:
			if kregex.search(p):
				keywords.add(k)
				for v in map[k].implies: keywords.add(v)
	return keywords

	
def projectizeTags(tokens):
	map = getMap()
	for i in range(len(tokens)):
		if 'project-' + tokens[i] in map:
			tokens[i] = 'project-' + tokens[i]
	return tokens

