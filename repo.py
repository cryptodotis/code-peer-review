#!/usr/bin/python

import time, MySQLdb

from database import DB

class Repo:
    id = 0
    type = 0
    url = ''
    
    initialized = False
    def __init__(self):
        pass
    
    def loadFromDatabase(self, row):
        self.initialized = True
        
        self.id = row[DB.repo.id]
        self.name = row[DB.repo.name]
        self.type = row[DB.repo.repotypeid]
        self.url = row[DB.repo.url]
        self.viewlink = row[DB.repo.viewlink]
        self.tagname = row[DB.repo.tagname]
        self.tagmaturity = row[DB.repo.tagmaturity]
        
    def loadFromValues(self, i, n, t, u, vl, tagn, tagm):
        self.initialized = True
        
        self.id = i
        self.name = n
        self.type = t
        self.url = u
        self.viewlink = vl
        self.tagname = tagn
        self.tagmaturity = tagm
        
    def getpprint(self):
        if not self.initialized:
            raise Exception("called getBasePath on unitialized Commit object")
            
        s = "(" + str(self.id) + ", " + self.name + ", "
        
        for i in dir(Repo.Type):
            if self.type == getattr(Repo.Type, i):
                s += i
        
        s+= ", " + self.url + ", project-" + self.tagname + ", maturity-" + self.tagmaturity + ")"
        return s
    def pprint(self):
        print self.getpprint()
        
                
    class Type:
        SVN = 1
        GIT = 2
        CVS = 3
        RSS = 4
        EMAIL = 5
        BAZAAR = 6
        MERCURIAL = 7
        TAR = 8
        DARCS = 9
    
    #Maturity Values
    #	pervasive - project is used by hundreds or thousands of people who regurally rely on it for protection
    #	stable - project is in use and stable on public servers, but not pervasive
    #	beta - project can be used on public servers but is marked as beta by the authors
    #	development - project is in development
