#!/usr/bin/python
import argparse, sys, time, os
import pysvn

from common import *
from svncommit import SVNCommit
from repo import Repo

def getCommits(repo, startdate, enddate):
    end_rev = pysvn.Revision(pysvn.opt_revision_kind.date, enddate)
    start_rev = pysvn.Revision(pysvn.opt_revision_kind.date, startdate)
    
    client = pysvn.Client()

    commits = []
    msgs = client.log(repo.url, revision_start=start_rev, revision_end=end_rev, discover_changed_paths=True)
    msgs.reverse() 
    for m in msgs:
        date = m.data['revprops']['svn:date']
        message = m.data['message']
        paths = [p.path for p in m.data['changed_paths']]

        c = SVNCommit()
        alldiffs = c.getChangedTexts((m.data['revision'].number, repo))
        c.loadFromSource(repo, message, date, paths, m.data['revision'].number, alldiffs)
        commits.append(c)
    return commits

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Given a repo url, a startdate and enddate, process the commits between.')
    parser.add_argument('repo')
    parser.add_argument('startdate')
    parser.add_argument('enddate')
    args = parser.parse_args()
    
    args.startdate, args.enddate = fixDates(args.startdate, args.enddate)
    
    r = Repo()
    r.loadFromValues(-1, Repo.Type.SVN, args.repo, '', '', '')
    commits = getCommits(r, args.startdate, args.enddate)
    for c in commits: 
        c.pprint()
        c.save()
