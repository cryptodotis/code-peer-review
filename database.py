#!/usr/bin/python

import MySQLdb

from config import Config

class DB:
	@staticmethod
	def getConn():
		conn = MySQLdb.connect (host = Config.host,
                	                user = Config.username,
                	                passwd = Config.password,
                	                db = Config.database)
		return conn
	
	#define table names and column indices
	class repotype:
		_table = "repotype_tbl"
		id = 0
		type = 1
	class repo:
		_table = "repo_tbl"
		id = 0
		repotypeid = 1
		url = 2
		tagname = 3
		tagmaturity = 4
	class keyword:
		_table = "keyword_tbl"
		keyword = 0
		parent = 1
	class commit:
		_table = "commit_tbl"
		id = 0
		repoid = 1
		date = 2
		message = 3
		uniqueid = 4
	class commitfile:
		_table = "commitfile_tbl"
		commitid = 0
		file = 1
	class commitkeyword:
		_table = "commitkeyword_tbl"
		commitid = 0
		keyword = 1
