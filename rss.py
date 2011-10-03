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

class MainHandler(tornado.web.RequestHandler):
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

application = tornado.web.Application([
    (r"/(.*)", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

		
		
