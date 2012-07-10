#!/usr/bin/python

import MySQLdb, argparse, time

from common import *
from config import Config
from database import DB
from repo import Repo
from commit import Commit
import svnpuller, gitpuller

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Given a startdate and enddate, process the commits between for all repos in the database.')
    parser.add_argument('startdate')
    parser.add_argument('enddate')
    args = parser.parse_args()
    
    args.startdate, args.enddate = fixDates(args.startdate, args.enddate)

    print "Searching between", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(args.startdate)), "-", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(args.enddate))
    
    conn = DB.getConn()
    c = conn.cursor()
    
    c.execute("SELECT * FROM " + DB.repo._table)
    rows = c.fetchall()
    
    for i in rows:
        r = Repo()
        r.loadFromDatabase(i)
        r.pprint()
        
        module = -1
        if r.type == Repo.Type.SVN:
            module = svnpuller
        elif r.type == Repo.Type.GIT:
            module = gitpuller
            
        if module != -1:
            try:
                commits = module.getCommits(r, args.startdate, args.enddate)
            except:
                print "Error pulling commits for", r.url
                commits = []
                
            for c in commits:
                print ".",
                c.save()
            if commits: print ""
        else:
            print "Do not have a module for", r.url
