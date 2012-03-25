#!/usr/bin/python

import MySQLdb, time

from common import *
from config import Config
from database import DB
from keywordsfilter import *

from repo import Repo
from commit import Commit
from gitcommit import GitCommit
from svncommit import SVNCommit

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
                
                DB.execute(c, "SELECT * from " + DB.commitdiffs._table + " WHERE commitid IN (" + allcommitids + ")")
                commitdata = c.fetchall()
                

        commits = []
        for i in commitrows:
                r = Repo()
                r.loadFromValues(i[DB.commit._numColumns + DB.repo.id], i[DB.commit._numColumns + DB.repo.name], i[DB.commit._numColumns + DB.repo.repotypeid], i[DB.commit._numColumns + DB.repo.url],
                        i[DB.commit._numColumns + DB.repo.viewlink], i[DB.commit._numColumns + DB.repo.tagname], i[DB.commit._numColumns + DB.repo.tagmaturity])

                files = [file[DB.commitfile.file] for file in commitfiles
                        if file[DB.commitfile.commitid] == i[DB.commit.id]]
                keywords = [keyword[DB.commitkeyword.keyword] for keyword in commitkeywords
                            if keyword[DB.commitkeyword.commitid] == i[DB.commit.id]]
                data = [cdata[DB.commitdiffs.data] for cdata in commitdata
                            if cdata[DB.commitdiffs.commitid] == i[DB.commit.id]][0]

                if i[DB.commit._numColumns + DB.repo.repotypeid] == Repo.Type.GIT:
                    c = GitCommit()
                elif i[DB.commit._numColumns + DB.repo.repotypeid] == Repo.Type.SVN:
                    c = SVNCommit()
                else:
                    c = Commit()
                c.loadFromDatabase(r, i, files, keywords, data)

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
            whereClause, components = keywordsTree.getEvaluationString('sql', "(SELECT ck.keyword FROM "+ DB.commitkeyword._table +" as ck WHERE ck.commitid = c.id)", "r.tagname", "r.maturity")
        
        getcommitsSQL += "WHERE " + whereClause + " "
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

    @staticmethod
    def findByKeywordsAndFulltext(keywords):
        getcommitsSQL = "SELECT c.*, r.* " + \
                "FROM " + DB.commit._table + " c " + \
                "INNER JOIN " + DB.repo._table + " r " + \
                "	ON r.id = c.repoid "
        
        whereClause = " 1=1 "
        components = []
        if keywords:
            keywordsTree = KeywordsParser(keywords)
            whereClause, components = keywordsTree.getEvaluationString('sql', "(SELECT ck.keyword FROM "+ DB.commitkeyword._table +" as ck WHERE ck.commitid = c.id)", "r.tagname", "r.maturity")
        
        getcommitsSQL += "WHERE " + whereClause
        getcommitsSQL += "ORDER BY c.date DESC "
        
        prelim_commits = DBQ.find(getcommitsSQL, components)
        if keywords and keywordsTree.anyFulltext():
            final_commits = []
            
            evalstr, evalcomponents = keywordsTree.getEvaluationString('eval', "c.dbkeywords", "'project-' + repo.tagname", "'maturity-' + repo.tagmaturity")
            evalstr = evalstr % tuple(evalcomponents)
            
            for c in prelim_commits:
                testResult = eval(evalstr)
                if testResult:
                    final_commits.append(c)
                
            return final_commits
        else:
            return prelim_commits
    @staticmethod
    def logTerms(ip, keywords):
        insertSQL = "INSERT INTO " + DB.searchqueries._table + "(timestamp, ip, terms) " + \
                        "VALUES(%s, INET_ATON(%s), %s) "
        conn = DB.getConn()
        c = conn.cursor()
        
        DB.execute(c, insertSQL, (int(time.time()), ip, keywords))
        