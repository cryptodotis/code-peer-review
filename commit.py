#!/usr/bin/python

import time, re, os, MySQLdb, unicodedata
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
		msg = re_gitsvn.sub('', msg)
		return msg.strip()

	def getBasePath(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		if not self.files: return ""

		trunks = [p for p in self.files if "/trunk" in p]
		branches = [p for p in self.files if "/branches" in p]
		tags = [p for p in self.files if "/tags" in p]
		odd = [p for p in self.files if p not in trunks and p not in branches and p not in tags]

		if ((1 if trunks else 0) + (1 if branches else 0) + \
			    (1 if tags else 0) + (1 if odd else 0)) > 1:
			ret = []
			if trunks: ret.append(os.path.commonprefix(trunks))
			if branches: ret.append(os.path.commonprefix(branches))
			if tags: ret.append(os.path.commonprefix(tags))
			if odd: ret.append(os.path.commonprefix(odd))
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
			lk = " " + k + " "
			pk = "/" + k
			
			if lk in log:
				keywords.add(k)
				for v in synonymmapping.map[k]: keywords.add(v)
			for p in paths:
				if pk in p:
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
		c.execute(sql, (self.repo.id, self.date, self.message, self.uniqueid))

		if not self.commitid:		
			self.commitid = conn.insert_id()

		if self.files:
			sql = "DELETE FROM " + DB.commitfile._table + " WHERE commitid = " + str(self.commitid)
			c.execute(sql)

			sql = "INSERT INTO " + DB.commitfile._table + "(commitid, file) "
			for f in self.files:
				sql += "SELECT " + str(self.commitid) + ", %s UNION "
			sql = sql[:-6]
			c.execute(sql, self.files)
		
		if self.dbkeywords:
			sql = "DELETE FROM " + DB.commitkeyword._table + " WHERE commitid = " + str(self.commitid)
			c.execute(sql)

			sql = "INSERT INTO " + DB.commitkeyword._table + "(commitid, keyword) "
			for f in self.dbkeywords:
				sql += "SELECT " + str(self.commitid) + ", %s UNION "
			sql = sql[:-6]
			c.execute(sql, [x for x in self.dbkeywords])

		conn.commit()
		
	def getpprint(self):
		if not self.initialized:
			raise Exception("called getBasePath on unitialized Commit object")
			
		eol = "\r\n"
		s = ""
		s += "ID:\t\t %s%s" % (self.uniqueid, eol)
		s += "Date:\t\t %s (%s)%s" % (unixToGitDateFormat(self.date), self.date, eol)
		s += "Log Message:\t %s%s" % (self.message, eol)
		if self.files:
			s += "Files:\t\t %s%s" % (self.files[0], eol)
			for p in self.files[1:]:
				s += "\t\t %s%s" % (p, eol)

		if self.base_paths and not isinstance(self.base_paths, basestring):
			s += "Base Paths:\t %s%s" % (self.base_paths[0], eol)
			for p in self.base_paths[1:]:
				s += "\t\t %s%s" % (p, eol)
		elif self.base_paths:
			s += "Base Path:\t %s%s" % (self.base_paths, eol)

		s+= "Keywords:\t %s%s" % (", ".join(self.keywords), eol)
		return s
	
	def pprint(self):
		print self.getpprint()
	
	def toRSSItem(self):
		title = self.repo.tagname
		if self.message and len(self.message) > 50: title += " - " + self.message[:50] + "..."
		elif self.message: title += " - " + self.message
		if self.dbkeywords: title += " - " + ",".join(self.dbkeywords)
		
		description  = "<pre>"
		description += self.getpprint()
		description += "</pre>"
		
		title = unicodedata.normalize('NFKD', unicode(title, 'utf-8')).encode('ascii', 'ignore')
		description = unicodedata.normalize('NFKD', unicode(description, 'utf-8')).encode('ascii', 'ignore')

		link = ''
		if self.repo.viewlink:
			link = self.repo.viewlink.replace('%ID', self.uniqueid)

		item = RSSItem(
			title = title,
			link = link,
			description = description,
			guid = self.repo.url + "#" + self.uniqueid,
			pubDate = unixToDatetime(self.date)
			)
		return item

