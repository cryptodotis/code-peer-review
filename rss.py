#!/usr/bin/python

import tornado.ioloop
import tornado.web

import MySQLdb, argparse, datetime
from PyRSS2Gen import RSS2

from common import *
from config import Config
from database import DB
from repo import Repo
from commit import Commit

class MainHandler(tornado.web.RequestHandler):
    def get(self):
	conn = DB.getConn()
	c = conn.cursor()
	
	c.execute("SELECT c.*, r.repotypeid, r.url, r.tagname, r.maturity FROM " + DB.commit._table + " c INNER JOIN " + DB.repo._table + " r ON r.id = c.repoid ORDER BY c.date DESC")
	commitrows = c.fetchall()
	
	allcommitids = ",".join([str(int(commit[0])) for commit in commitrows])
	
	#This is poor practice, but we assured ourselves the value is composed only of ints first
	c.execute("SELECT * from " + DB.commitfile._table + " WHERE commitid in (" + allcommitids + ")")
	commitfiles = c.fetchall()
	
	feed = RSS2(
		title = "Crypto.is Code Audit Feed",
		description = "Just a thing, right?",
		link = "https://crypto.is",
		lastBuildDate = datetime.datetime.utcnow()
		)
		

	for i in commitrows:
		r = Repo()
		r.loadFromValues(i[DB.commit.repoid], i[DB.commit._numColumns + 0], i[DB.commit._numColumns + 1], 
			i[DB.commit._numColumns + 2], i[DB.commit._numColumns + 3])
		
		files = [file[DB.commitfile.file] for file in commitfiles 
			if file[DB.commitfile.commitid] == i[DB.commit.id]]
		
		c = Commit()
		c.loadFromDatabase(r, i, files)

		feed.items.append(c.toRSSItem())
	
        self.set_header('Content-Type', 'application/rss+xml')
	self.write(feed.to_xml())
        return

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

		
		
