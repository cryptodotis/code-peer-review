#!/usr/bin/python
import argparse, sys, time, os
import pysvn

from common import *
from commit import Commit
from repo import Repo

svn_diff_header = re.compile('Index: .+\s=+\s-{3} .+\s\+{3} .+\s@@\ [0-9\-, \+]+@@\s+')
svn_diff_newline = re.compile('\\ No newline at end of file\s')
svn_diff_property = re.compile('Property changes on: .+\s_+\sAdded: .+\s\s+[\-\+]\s.+')
svn_diff_deletions = re.compile('^-.+$', re.MULTILINE)

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

        revnum = m.data['revision'].number
        if revnum == 1:
            diff = ''
        else:
            diff = client.diff(tmp_path='./', url_or_path=repo.url, revision1=pysvn.Revision(pysvn.opt_revision_kind.number, revnum-1), revision2=m.data['revision'])
            diff = svn_diff_header.sub('', diff)
            diff = svn_diff_newline.sub('', diff)
            diff = svn_diff_property.sub('', diff)
            diff = svn_diff_deletions.sub('', diff)
            diff = diff.lower()
            
        c = Commit()
        c.loadFromSource(repo, message, date, paths, m.data['revision'].number, [diff])
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
