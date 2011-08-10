#!/usr/bin/python

import MySQLdb

from config import Config
from database import DB
import svnpuller, gitpuller

if __name__ == "__main__":
	conn = DB.getConn()
	c = conn.cursor()
	
	c.execute("SELECT * FROM " + DB.repo._table)
	rows = c.fetchall()
	
	for r in rows:
		print r