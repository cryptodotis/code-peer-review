#!/usr/bin/python

import time, re, os, MySQLdb, unicodedata, cPickle, zlib
from PyRSS2Gen import RSSItem, Guid

from config import Config
import synonymmapping
from common import *
from database import DB
import gdiff

re_gitsvn = re.compile('git-svn-id: \w+://.+ \w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}-\w{4,12}')

svn_diff_header = re.compile('Index: .+\s=+\s-{3} .+\s\+{3} .+\s@@\ [0-9\-, \+]+@@\s+')
svn_diff_newline = re.compile('\\ No newline at end of file\s')
svn_diff_property = re.compile('Property changes on: .+\s_+\sAdded: .+\s\s+[\-\+]\s.+')
svn_diff_deletions = re.compile('^-.+$', re.MULTILINE)

punctuation = re.compile('[^a-zA-Z0-9 ]')

class Commit:
    repo = None
    message = ''
    date = 0
    files = []
    commitid = -1
    changedTexts = None
    changedTexts_data = None
    diffIsReallyBig = False

    initialized = False
    def __init__(self):
        self.changedTexts = None
        self.diffIsReallyBig = False
    
    def loadFromSource(self, repo, m, d, files, uid, diffs):
        self.initialized = True
    
        self.repo = repo
        self.rawmessage = Commit.cleanUpCommitMessage(m)
        self.message = self.rawmessage.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        self.date = d
        self.files = [f.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;") for f in files]
        self.uniqueid = uid

        self.base_paths = self.getBasePath()
        self.dbkeywords = self.getSynonyms(diffs)

        self.keywords = set(self.dbkeywords)
        self.keywords.add('project-' + repo.tagname)
        self.keywords.add('maturity-' + repo.tagmaturity)
    
    def loadFromDatabase(self, repo, row, files, keywords, data):
        self.initialized = True
        self.repo = repo
        self.commitid = row[DB.commit.id]
        self.rawmessage = row[DB.commit.message]
        self.message = self.rawmessage.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        self.date = row[DB.commit.date]
        self.uniqueid = row[DB.commit.uniqueid]

        self.files = [f.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;") for f in files]
        self.base_paths = self.getBasePath()
        self.dbkeywords = keywords

        self.keywords = set(self.dbkeywords)
        self.keywords.add('project-' + repo.tagname)
        self.keywords.add('maturity-' + repo.tagmaturity)
        
        self.changedTexts_data = data
        if self.changedTexts_data == 'TOOLARGE':
           self.diffIsReallyBig = True

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
    #Implemented in Child Classes
    #Returns an array of google diff structures used for google diff pretty-outputting
    def getDiffsArray(self):
        pass 
    #retrieves the metadata the child class needs for getChangedTexts from the populated object
    # during creation, this metadata is passed in independently and this is not called
    def getChangedTextMetadata(self):
        pass
    #Returns an array of changed texts used for synonym matching, not google's diff format
    def getChangedTexts(self, metadata):
        pass
    #/Implemented in Child Classes
    def _loadChangedTextFromBackingVar(self):
        if self.changedTexts != None:
           return self.changedTexts
        elif self.changedTexts_data == 'TOOLARGE':
           self.diffIsReallyBig = True
           self.changedTexts = []
        else:
           data = zlib.decompress(self.changedTexts_data)
           data = cPickle.loads(data)
           self.changedTexts = data
        return self.changedTexts
    def testFulltext(self, fulltext):
        #We don't want to fall back on an expensive operation in the subsequent function
        if self.changedTexts == None and self.changedTexts_data == None:
            raise Exception("called testFulltext prior to changedTexts_data being initialized")
        
        for d in self.getChangedTexts(None):
            if fulltext in d.lower(): return True
        
        return False
       
    def getPrettyDiffs(self):
        diffs = self.getDiffsArray()
        differ = gdiff.diff_match_patch()
        
        for d in diffs:
            differ.diff_cleanupSemantic(d)
            str = differ.diff_prettyHtml(d)
            if not isinstance(str, unicode):
               str = unicode(str, 'utf-8')
            else:
               str = str.encode('utf-8')
            yield str

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

        data = self.getChangedTexts(None)
        data = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)
        data = zlib.compress(data)

            
        sql = "DELETE FROM " + DB.commitdiffs._table + " WHERE commitid = " + str(self.commitid)
        c.execute(sql)

        sql = "INSERT INTO " + DB.commitdiffs._table + "(commitid, data) "
        sql += "VALUES(" + str(self.commitid) + ", %s)"
        c.execute(sql, [data])
        
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

        sql = "DELETE FROM " + DB.commitwordmap._table + " WHERE commitid = " + str(self.commitid)
        c.execute(sql)

        data = self.getChangedTexts(None)
        data.append(self.rawmessage.lower())
        data.extend([f.lower() for f in self.files])
        data = [punctuation.sub(' ', d) for d in data]

        allwords = set()
        for d in data:
            dWords = d.split()
            dTotalIndex = 0
            while dTotalIndex < len(dWords):
                words = []
                dThisIndex = 0
                sql = "INSERT INTO " + DB.commitwordmap._table + "(commitid, word) "                
                while dThisIndex < 500 and dTotalIndex < len(dWords):
                    w = dWords[dThisIndex][:50]
                    if len(w) > 2 and w not in allwords:
                        sql += "SELECT " + str(self.commitid) + ", %s UNION "
                        words.append(w)
                        allwords.add(w)
                    dThisIndex += 1
                    dTotalIndex += 1
                sql = sql[:-6]
                if words:
                    DB.execute(c, sql, words)

        conn.commit()
        
    def getpprint(self, link=False):
        if not self.initialized:
            raise Exception("called getpprint on unitialized Commit object")
            
        eol = "\r\n"
        s = ""
        s += "Project:\t %s%s" % (self.repo.name, eol)
        if link:
            s += "Project URL:\t <a href=\"%s\">%s</a>%s" % (self.repo.url, self.repo.url, eol)
        else:
            s += "Project URL:\t %s %s" % (self.repo.url, eol)
        s += "Commit Date:\t %s (%s)%s" % (unixToGitDateFormat(self.date), self.date, eol)
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
        
        internallink = Config.rooturl + "/commit/" + self.repo.tagname + "/" + self.uniqueid
        if link:
            s += "Internal:\t <a href=\"%s\">%s</a>%s" % (internallink, internallink, eol)
        else:
            s += "Internal:\t %s%s" % (internallink, eol)
        
        if self.repo.viewlink:
            externallink = self.repo.viewlink.replace('%ID', self.uniqueid)
            if link:
                s += "External:\t <a href=\"%s\">%s</a>%s" % (externallink, externallink, eol)
            else:
                s += "External:\t %s%s" % (externallink, eol)
        return s
    
    def pprint(self):
        print self.getpprint(False)
    
    def toRSSItem(self):
        title = self.repo.tagname
        if self.rawmessage and len(self.rawmessage) > 50: title += " - " + self.rawmessage[:50] + "..."
        elif self.rawmessage: title += " - " + self.rawmessage
        if self.dbkeywords: title += " - " + ",".join(self.dbkeywords)
        
        description  = "<pre>"
        description += self.getpprint(True)
        description += "</pre>"
        
	if type(title) != unicode:
		title = unicode(title, 'utf-8')
	if type(description) != unicode:
		description = unicode(description, 'utf-8')
        title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
        description = unicodedata.normalize('NFKD', description).encode('ascii', 'ignore')

        guid = Config.rooturl + "/commit/" + self.repo.tagname + "/" + self.uniqueid
        link = ''
        if self.repo.viewlink:
            link = self.repo.viewlink.replace('%ID', self.uniqueid)
        else:
            link = guid

        item = RSSItem(
            title = title,
            link = link,
            description = description,
            guid = Guid(guid, isPermaLink=0),
            pubDate = unixToDatetime(self.date)
            )
        return item

