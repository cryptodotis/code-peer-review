#!/usr/bin/python

import tornado.ioloop
import tornado.web

import MySQLdb, argparse, datetime, unicodedata
from PyRSS2Gen import RSS2

from common import *
from config import Config
from database import DB
from databaseQueries import DBQ
from repo import Repo
from commit import Commit
from keywordsfilter import *

class RSSHandler(tornado.web.RequestHandler):
	def get(self, keywords):
		commits = DBQ.findByKeywords(keywords)
		
		feed = RSS2(
			title = "Crypto.is Code Audit Feed",
			description = "Just a thing, right?",
			link = "https://crypto.is",
			lastBuildDate = datetime.datetime.utcnow()
			)
			

		for c in commits:
			feed.items.append(c.toRSSItem())
		
		self.set_header('Content-Type', 'application/rss+xml')
		
		xml = feed.to_xml()
		self.write(xml)
		return

class CommitHandler(tornado.web.RequestHandler):
	def get(self, project, uniqueid):
		commit = DBQ.findByIDs(project, uniqueid)
		if len(commit) > 1:
			raise "More than one commit returned?"
		if not commit:
			self.write("Could not find commit")
			return
		commit = commit[0]		

		feed = RSS2(
			title = "Crypto.is Code Audit Feed",
			description = "Just a thing, right?",
			link = "https://crypto.is",
			lastBuildDate = datetime.datetime.utcnow()
			)
			
		feed.items.append(commit.toRSSItem())
		
		self.set_header('Content-Type', 'application/rss+xml')
		
		xml = feed.to_xml()
		self.write(xml)
		return

application = tornado.web.Application([
    (r"/rss/(.*)", RSSHandler),
    (r"/commit/(.*)/(.*)", CommitHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

		
		
