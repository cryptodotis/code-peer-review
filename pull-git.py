#!/usr/bin/python
import argparse, sys, time, os
import git as pygit

from common import *

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
		date = m.committed_date
		message = cleanUpCommitMessage(m.message)
		paths = []

		if m.committed_date > args.enddate: continue
	
		print "Date:\t\t", unixToGitDateFormat(date), "(" + str(date) + ")"
		print "Log Message:\t", message

		files = m.stats.files.keys()
		if len(files) > 0: paths.append(files[0]) 
		for p in files[1:]:
			paths.append(p)
		base_paths = getBasePath(paths)
		
		if len(base_paths) > 0: 
			if len(base_paths) > 0 and not isinstance(base_paths, basestring):
				print "Base Paths:\t", base_paths[0]
				for p in base_paths[1:]:
					print "\t\t", p
			else:
				print "Base Path:\t", base_paths
		if len(paths) > 0: 
			print "Paths:\t\t", paths[0] 
			for p in paths[1:]:
				print "\t\t", p
		print "Keywords:\t", ", ".join(getSynonyms(message, paths))
		print ""
