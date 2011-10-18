#/usr/bin/python

import MySQLdb
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
				map[r[DB.keyword.keyword]] = []
			if r[DB.keyword.parent]:
		   		map[r[DB.keyword.keyword]].append(r[DB.keyword.parent])
				if not r[DB.keyword.parent] in map:
					map[r[DB.keyword.parent]] = []

		c.execute("SELECT tagname FROM " + DB.repo._table)
		rows = c.fetchall()
		for r in rows:
			if not 'project-' + r[0] in map:
				map['project-' + r[0]] = []
    
    	return map
