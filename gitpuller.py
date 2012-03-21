#!/usr/bin/python
import argparse, sys, time, os
import git as pygit
import gdiff

from common import *
from config import *
from gitcommit import GitCommit
#from commit import Commit
from repo import Repo

def getCommits(repo, startdate, enddate):
    localfolder = urlToFolder(repo.url)
    differ = gdiff.diff_match_patch()

    repoloc = Config.fsdir + 'git-repos/' + localfolder + '/'
    if os.path.exists(repoloc):
        c = pygit.Repo(repoloc)
    else:
        os.makedirs(repoloc)
        c = pygit.Repo.init(repoloc)
        c.create_remote('origin', repo.url)

    c.remotes.origin.fetch()
    c.remotes.origin.pull('master')

    commits = []
    msgs = c.iter_commits(since=unixToGitDateFormat(startdate))
    for m in msgs:
        if m.committed_date > enddate: continue
        
        # TODO BUG: We are unable to get a git diff of the first commit.
        #   http://osdir.com/ml/version-control.git/2005-05/msg01309.html
        #   http://git.661346.n2.nabble.com/git-diff-tree-against-the-root-commit-td5685272.html
        if not m.parents: continue

        c = GitCommit()
        alldiffs = c.getChangedTexts(m)
        c.loadFromSource(repo, m.message, m.committed_date, m.stats.files.keys(), m.__str__(), alldiffs)
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
    r.loadFromValues(-1, "", Repo.Type.GIT, args.repo, '', '', '')
    commits = getCommits(r, args.startdate, args.enddate)
    for c in commits: 
        print "========================================="
        c.pprint()
        c.save()
