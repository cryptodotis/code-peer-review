#!/usr/bin/python

import tornado.ioloop
import tornado.web
import tornado.options
import logging

import MySQLdb, argparse, datetime, unicodedata, time
from PyRSS2Gen import RSS2
from jinja2 import Environment, FileSystemLoader

from common import *
from config import Config
from database import DB
from databaseQueries import DBQ
from repo import Repo
from commit import Commit
from keywordsfilter import *

def getFeed():
    feed = RSS2(
            title = "Crypto.is Code Audit Feed",
            description = "Just a thing, right?",
            link = "https://crypto.is",
            lastBuildDate = datetime.datetime.utcnow()
            )
    return feed

class RSSHandler(tornado.web.RequestHandler):
    def get(self, keywords):
        fiveDaysAgo = time.time() - (5 * 24 * 60 * 60)
        commits = DBQ.findByKeywordsAndFulltext(keywords, fiveDaysAgo)
        feed = getFeed()

        for c in commits:
            feed.items.append(c.toRSSItem())
        
        self.set_header('Content-Type', 'application/rss+xml')
        
        xml = feed.to_xml()
        self.write(xml)
        return

class KeywordsHandler(tornado.web.RequestHandler):
    def get(self, keywords):
        commits = DBQ.findByKeywords(keywords)
        feed = getFeed()

        for c in commits:
            feed.items.append(c.toRSSItem())
        
        self.set_header('Content-Type', 'application/rss+xml')
        
        xml = feed.to_xml()
        self.write(xml)
        return

class LandingHandler(tornado.web.RequestHandler):
    def get(self):
        commits=[]
        template = env.get_template('search.html')
        html = template.render(commits=commits)	
        self.write(html)
        return

class HallOfFameHandler(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template('halloffame.html')
        html = template.render()	
        self.write(html)
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

        template = env.get_template('commit.html')
        html = template.render(commit=commit)	
        
        self.write(html)
        return

class SearchHandler(tornado.web.RequestHandler):
    def get(self, keywords):
        commits = []
        if not keywords:
            template = env.get_template('search.html')
        else:
            DBQ.logTerms(self.request.remote_ip, keywords)
            commits = DBQ.findByKeywordsAndFulltext(keywords)
            template = env.get_template('searchresults.html')
        
        html = template.render(commits=commits, rsssearchparams=keywords)	
        self.write(html)
        return
    def post(self, keywords):
        keywords = self.request.arguments['terms'][0]
        DBQ.logTerms(self.request.remote_ip, keywords)
        commits = DBQ.findByKeywordsAndFulltext(keywords)
        template = env.get_template('searchresults.html')
        
        html = template.render(commits=commits, rsssearchparams=keywords)	
        self.write(html)
        return

env = Environment(autoescape=True,
                  loader=FileSystemLoader(Config.fsdir + 'templates'))

application = tornado.web.Application([
    (r"/", LandingHandler),
    (r"/search/?(.*)", SearchHandler),
    (r"/commit/(.*)/(.*)", CommitHandler),
    (r"/halloffame", HallOfFameHandler),
    (r"/keywords/(.*)", KeywordsHandler),#Obsolete, For testing only
    (r"/rss/(.*)", RSSHandler),
])
tornado.options.parse_command_line() 

if __name__ == "__main__":
    tlog = logging.FileHandler(Config.logfile)
    logging.getLogger().addHandler(tlog)
    logging.debug('Starting up...')
    
    application.listen(Config.tornadoport)
    tornado.ioloop.IOLoop.instance().start()

        
        
