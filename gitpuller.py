#!/usr/bin/python
import argparse, sys, time, os
import git as pygit

from common import *
from commit import Commit

def getCommits(repo, startdate, enddate):
	localfolder = urlToFolder(repo)

	repoloc = 'git-repos/' + localfolder + '/'
	if os.path.exists(repoloc):
		c = pygit.Repo(repoloc)
	else:
		os.makedirs(repoloc)
		c = pygit.Repo.init(repoloc)
		c.create_remote('origin', repo)

	c.remotes.origin.fetch()
	c.remotes.origin.pull('master')

	commits = []
	msgs = c.iter_commits(since=unixToGitDateFormat(startdate))
	for m in msgs:
		if m.committed_date > enddate: continue

		date = m.committed_date
		message = cleanUpCommitMessage(m.message)
		files = m.stats.files.keys()

		c = Commit(message, date, files)
		commits.append(c)
	return commits

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Given a repo url, a startdate and enddate, process the commits between.')
	parser.add_argument('repo')
	parser.add_argument('startdate')
	parser.add_argument('enddate')
	args = parser.parse_args()
	
	args.startdate, args.enddate = fixDates(args.startdate, args.enddate)
	
	commits = getCommits(args.repo, args.startdate, args.enddate)
	for c in commits: c.pprint()
