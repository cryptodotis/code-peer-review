#!/usr/bin/python

import MySQLdb

from common import *
from config import Config
from database import DB
from repo import Repo
from commit import Commit
from keywordsfilter import *

class DBQ:
    @staticmethod
    def find(query, components):
        conn = DB.getConn()
        c = conn.cursor()
        
        c.execute(query, components)
                commitrows = c.fetchall()
                commitfiles = []

                if commitrows:
                        allcommitids = ",".join([str(int(commit[0])) for commit in commitrows])

                        #This is poor practice, but we assured ourselves the value is composed only of ints first
                        DB.execute(c, "SELECT * from " + DB.commitfile._table + " WHERE commitid IN (" + allcommitids + ")")
                        commitfiles = c.fetchall()

                        DB.execute(c, "SELECT * from " + DB.commitkeyword._table + " WHERE commitid IN (" + allcommitids + ")")
                        commitkeywords = c.fetchall()

                commits = []
                for i in commitrows:
                        r = Repo()
                        r.loadFromValues(i[DB.commit._numColumns + 0], i[DB.commit._numColumns + 1], i[DB.commit._numColumns + 2],
                                i[DB.commit._numColumns + 3], i[DB.commit._numColumns + 4], i[DB.commit._numColumns + 5])

                        files = [file[DB.commitfile.file] for file in commitfiles
                                if file[DB.commitfile.commitid] == i[DB.commit.id]]
                        keywords = [keyword[DB.commitkeyword.keyword] for keyword in commitkeywords
                                    if keyword[DB.commitkeyword.commitid] == i[DB.commit.id]]

                        c = Commit()
                        c.loadFromDatabase(r, i, files, keywords)

                        commits.append(c)

                return commits

    @staticmethod
    def findByKeywords(keywords):
        getcommitsSQL = "SELECT c.*, r.* " + \
                "FROM " + DB.commit._table + " c " + \
                "INNER JOIN " + DB.repo._table + " r " + \
                "	ON r.id = c.repoid "
        
        whereClause = " 1=1 "
        components = []
        if keywords:
            keywordsTree = KeywordsParser(keywords)
            getcommitsSQL += "LEFT OUTER JOIN " + DB.commitkeyword._table + " ck " + \
                             "	ON c.id = ck.commitid "
            whereClause, components = keywordsTree.getWhereClause("ck.keyword", "r.tagname", "r.maturity")
        
        getcommitsSQL += "WHERE " + whereClause
        getcommitsSQL += "ORDER BY c.date DESC "
        
        return DBQ.find(getcommitsSQL, components)

    @staticmethod
    def findByIDs(project, uniqueid):
        getcommitsSQL = "SELECT c.*, r.* " + \
                "FROM " + DB.commit._table + " c " + \
                "INNER JOIN " + DB.repo._table + " r " + \
                "	ON r.id = c.repoid "
        
        whereClause = " 1=1 "
        components = []
        if project and uniqueid:
            whereClause += "AND r.tagname = %s AND c.uniqueid = %s "
            components = [project, uniqueid]
        
        getcommitsSQL += "WHERE " + whereClause
        getcommitsSQL += "ORDER BY c.date DESC "
        
        return DBQ.find(getcommitsSQL, components)

