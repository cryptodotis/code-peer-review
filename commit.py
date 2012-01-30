#!/usr/bin/python

import time, re, os, MySQLdb, unicodedata
from PyRSS2Gen import RSSItem

from config import Config
import synonymmapping
from common import *
from database import DB
import gdiff
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
    
    def loadFromSource(self, repo, m, d, f, uid, diffs):
        self.initialized = True
    
        self.repo = repo
        self.message = Commit.cleanUpCommitMessage(m)
        self.date = d
        self.files = f
        self.uniqueid = uid

        self.base_paths = self.getBasePath()
        self.dbkeywords = self.getSynonyms(diffs)

        self.keywords = set(self.dbkeywords)
        self.keywords.add('project-' + repo.tagname)
        self.keywords.add('maturity-' + repo.tagmaturity)
    
    def loadFromDatabase(self, repo, row, files, keywords):
        self.initialized = True
        
        self.repo = repo
        self.commitid = row[DB.commit.id]
        self.message = row[DB.commit.message]
        self.date = row[DB.commit.date]
        self.uniqueid = row[DB.commit.uniqueid]

        self.files = files
        self.base_paths = self.getBasePath()
        self.dbkeywords = keywords

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

        paths = set()
        for f in self.files:
            paths.add(os.path.dirname(f))
        l = [p for p in paths if p]
        l.sort()
        return l

    def getSynonyms(self, diffs):
        if not self.initialized:
            raise Exception("called getSynonyms on unitialized Commit object")
            
        keywords = synonymmapping.getTags(self, diffs)

        return keywords

    def save(self):
        if not self.initialized:
            raise Exception("called save on unitialized Commit object")
            
        conn = DB.getConn()
        c = conn.cursor()
        sql = "INSERT INTO " + DB.commit._table + """(repoid, date, message, uniqueid) 
                VALUES(%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE uniqueid = VALUES(uniqueid)""" 
        c.execute(sql, (self.repo.id, self.date, self.message, self.uniqueid))

        if self.commitid <= 0:
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
            raise Exception("called getpprint on unitialized Commit object")
            
        eol = "\r\n"
        s = ""
        s += "=========================================%s" % (eol)
        s += "Date:\t\t %s (%s)%s" % (unixToGitDateFormat(self.date), self.date, eol)
        s += "Log Message:\t %s%s" % (self.message, eol)
        s += eol + eol
        if self.files:
            s += "Files:\t\t %s%s" % (self.files[0], eol)
            for p in self.files[1:14]:
                s += "\t\t %s%s" % (p, eol)
            if len(self.files) > 15:
                s += "\t\t ...%s" % (eol)
        if self.base_paths:
            plural = len(self.base_paths) > 1
            s += "Base Path%s:\t %s%s" % ("s" if plural else "", self.base_paths[0], eol)
            for p in self.base_paths[1:]:
                s += "\t\t %s%s" % (p, eol)

        s += "Keywords:\t %s%s" % (", ".join(self.keywords), eol)
        s += "ID:\t\t %s%s" % (self.uniqueid, eol)
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
            guid = Config.rooturl + "/commit/" + self.repo.tagname + "/" + self.uniqueid,
            pubDate = unixToDatetime(self.date)
            )
        return item

