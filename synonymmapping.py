#/usr/bin/python

import MySQLdb
from database import DB

map = None

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
