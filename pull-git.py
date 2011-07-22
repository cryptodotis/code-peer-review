#!/usr/bin/python
import argparse, sys, time, os
import git as pygit

from common import *
from commit import Commit

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Given a repo url, a startdate and enddate, process the commits between.')
	parser.add_argument('repo')
	parser.add_argument('startdate')
	parser.add_argument('enddate')
	args = parser.parse_args()
	
	args.startdate, args.enddate = fixDates(args.startdate, args.enddate)
	localfolder = urlToFolder(args.repo)

	repoloc = 'git-repos/' + localfolder + '/'
	if os.path.exists(repoloc):
		c = pygit.Repo(repoloc)
	else:
		os.makedirs(repoloc)
		c = pygit.Repo.init(repoloc)
		c.create_remote('origin', args.repo)

	c.remotes.origin.fetch()
	c.remotes.origin.pull('master')

	msgs = c.iter_commits(since=unixToGitDateFormat(args.startdate))
	for m in msgs:
		if m.committed_date > args.enddate: continue

		date = m.committed_date
		message = cleanUpCommitMessage(m.message)
		files = m.stats.files.keys()

		c = Commit(message, date, files)
		c.pprint()

