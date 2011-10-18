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
	@staticmethod
	def execute(c, sql, *args):
		try:
			if not args:
				c.execute(sql)
			else:
				c.execute(sql, args[0])
		except MySQLdb.OperationalError as e:
			print e
			print sql
			if args:
				print args[0]
			raise e
	#@staticmethod
	#def execute(c, sql, args):
	#	try:
	#		c.execute(sql, args)
	#	except _mysql_exceptions.OperationError as e:
	#		print e
	#		print sql, args
	#		raise e
	
	#define table names and column indices
	class repotype:
		_table = "repotype_tbl"
		id = 0
		type = 1
		_numColumns = 2
	class repo:
		_table = "repo_tbl"
		id = 0
		repotypeid = 1
		url = 2
		viewlink = 3
		tagname = 4
		tagmaturity = 5
		_numColumns = 6
	class keyword:
		_table = "keyword_tbl"
		keyword = 0
		parent = 1
		type = 2
		_numColumns = 3
	class commit:
		_table = "commit_tbl"
		id = 0
		repoid = 1
		date = 2
		message = 3
		uniqueid = 4
		_numColumns = 5
	class commitfile:
		_table = "commitfile_tbl"
		commitid = 0
		file = 1
		_numColumns = 2
	class commitkeyword:
		_table = "commitkeyword_tbl"
		commitid = 0
		keyword = 1
		_numColumns = 2

