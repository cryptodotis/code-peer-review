#!/usr/bin/python

import time, re, os, MySQLdb
from PyRSS2Gen import RSSItem

import synonymmapping
from common import *
from database import DB
re_gitsvn = re.compile('git-svn-id: \w+://.+ \w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}')

class Commit:
	repo = None
	message = ''
	date = 0
	files = []
	commitid = -1
	
	initialized = False
	def __init__(self):
		pass
	
	def loadFromSource(self, repo, m, d, f, uid):
		self.initialized = True
	
		self.repo = repo
		self.message = Commit.cleanUpCommitMessage(m)
		self.date = d
		self.files = f
		self.uniqueid = uid

		self.base_paths = self.getBasePath()
		self.dbkeywords = self.getSynonyms()

		self.keywords = set(self.dbkeywords)
		self.keywords.add('project-' + repo.tagname)
		self.keywords.add('maturity-' + repo.tagmaturity)
	
	def loadFromDatabase(self, repo, row, files):
		self.initialized = True
		
		self.repo = repo
		self.commitid = row[DB.commit.id]
		self.message = row[DB.commit.message]
		self.date = row[DB.commit.date]
		self.uniqueid = row[DB.commit.uniqueid]

		self.files = files
		self.base_paths = self.getBasePath()
		self.dbkeywords = self.getSynonyms()

		self.keywords = set(self.dbkeywords)
		self.keywords.add('project-' + repo.tagname)
		self.keywords.add('maturity-' + repo.tagmaturity)

	@staticmethod
	def cleanUpCommitMessage(msg):
		msg = re.sub(re_gitsvn, '', msg)
		return msg.strip()

	def getBasePath(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		if len(self.files) == 0: return ""
		trunks = [p for p in self.files if "/trunk" in p]
		branches = [p for p in self.files if "/branches" in p]
		tags = [p for p in self.files if "/tags" in p]
		odd = [p for p in self.files if p not in trunks and p not in branches and p not in tags]
		if ((1 if len(trunks) > 0 else 0) + (1 if len(branches) > 0 else 0) + \
				(1 if len(tags) > 0 else 0) + (1 if len(odd) > 0 else 0)) > 1:
				ret = []
				if len(trunks) > 0: ret.append(os.path.commonprefix(trunks))
				if len(branches) > 0: ret.append(os.path.commonprefix(branches))
				if len(tags) > 0: ret.append(os.path.commonprefix(tags))
				if len(odd) > 0: ret.append(os.path.commonprefix(odd))
				return ret
		else:
				return os.path.dirname(os.path.commonprefix(self.files))


	def getSynonyms(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		log = self.message.lower()
		paths = []
		for i in range(len(self.files)): paths.append(self.files[i].lower())

		keywords = set()
		for k in synonymmapping.getMap():
				if k in log:
						keywords.add(k)
						for v in synonymmapping.map[k]: keywords.add(v)
				for p in paths:
						if k in p:
								keywords.add(k)
								for v in synonymmapping.map[k]: keywords.add(v)

		return keywords

	def save(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		conn = DB.getConn()
		c = conn.cursor()
		sql = "INSERT INTO " + DB.commit._table + """(repoid, date, message, uniqueid) 
				VALUES(%s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE uniqueid = VALUES(uniqueid)""" 
		c.execute(sql, (self.repoid, self.date, self.message, self.uniqueid))

		self.commitid = conn.insert_id()

		if len(self.files):
			sql = "INSERT INTO " + DB.commitfile._table + "(commitid, file) "
			for f in self.files:
				sql += "SELECT " + str(self.commitid) + ", %s UNION "
			sql = sql[:-6]
			c.execute(sql, self.files)
		
		if(len(self.dbkeywords)):
			sql = "INSERT INTO " + DB.commitkeyword._table + "(commitid, keyword) "
			for f in self.dbkeywords:
				sql += "SELECT " + str(self.commitid) + ", %s UNION "
			sql = sql[:-6]
			c.execute(sql, [x for x in self.dbkeywords])

		conn.commit()
		
	def pprint(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		print "ID:\t\t", self.uniqueid
		print "Date:\t\t", unixToGitDateFormat(self.date), "(" + str(self.date) + ")"
		print "Log Message:\t", self.message
		if len(self.files) > 0:
			print "Files:\t\t", self.files[0]
			for p in self.files[1:]:
				print "\t\t", p

		if len(self.base_paths) > 0:
			if len(self.base_paths) > 0 and not isinstance(self.base_paths, basestring):
				print "Base Paths:\t", self.base_paths[0]
				for p in self.base_paths[1:]:
					print "\t\t", p
				else:
					print "Base Path:\t", self.base_paths
		print "Keywords:\t", ", ".join(self.keywords)
		
	def toRSSItem(self):
		item = RSSItem(
			title = self.message,
			link = self.repo.url,
			description = self.message,
			guid = self.repo.url + "#" + self.uniqueid,
			pubDate = unixToDatetime(self.date)
			)
		return item

