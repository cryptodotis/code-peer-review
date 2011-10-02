#!/usr/bin/python

import MySQLdb, argparse, datetime, unicodedata

from common import *
from config import Config
from database import DB
from repo import Repo
from commit import Commit
from keywordsfilter import *

def browse(keywords):
	conn = DB.getConn()
	c = conn.cursor()
	
	getcommitsSQL = "SELECT c.*, r.repotypeid, r.url, r.tagname, r.maturity " + \
					"FROM " + DB.commit._table + " c " + \
					"INNER JOIN " + DB.repo._table + " r " + \
					"	ON r.id = c.repoid "
	
	whereClause = " 1=1 "
	components = []
	if keywords:
		keywordsTree = KeywordsParser(keywords)
		getcommitsSQL += "LEFT OUTER JOIN " + DB.commitkeyword._table + " ck " + \
						 "	ON c.id = ck.commitid "
		whereClause, components = keywordsTree.getWhereClause("ck.keyword", "r.tagname", "r.maturity")
	
	getcommitsSQL += "WHERE " + whereClause
	getcommitsSQL += "ORDER BY c.date DESC "
	
	c.execute(getcommitsSQL, components)
	commitrows = c.fetchall()
	
	if commitrows:
		allcommitids = ",".join([str(int(commit[0])) for commit in commitrows])
	
		#This is poor practice, but we assured ourselves the value is composed only of ints first
		c.execute("SELECT * from " + DB.commitfile._table + " WHERE commitid IN (" + allcommitids + ")")
		commitfiles = c.fetchall()
	
	for i in commitrows:
		r = Repo()
		r.loadFromValues(i[DB.commit.repoid], i[DB.commit._numColumns + 0], i[DB.commit._numColumns + 1], 
			i[DB.commit._numColumns + 2], i[DB.commit._numColumns + 3])
		
		files = [file[DB.commitfile.file] for file in commitfiles 
			if file[DB.commitfile.commitid] == i[DB.commit.id]]
		
		c = Commit()
		c.loadFromDatabase(r, i, files)
		
		c.pprint()

if __name__ == "__main__":
	if sys.argv:
		browse(" ".join(sys.argv[1:]))
	else:
		browse('')

		
		
