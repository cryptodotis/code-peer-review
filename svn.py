#!/usr/bin/python
import argparse, sys, time, os
import pysvn

from common import *

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Given a repo url, a startdate and enddate, process the commits between.')
	parser.add_argument('repo')
	parser.add_argument('startdate')
	parser.add_argument('enddate')
	args = parser.parse_args()
	
	args.startdate, args.enddate = fixDates(args.startdate, args.enddate)
	
	end_rev = pysvn.Revision(pysvn.opt_revision_kind.date, args.enddate)
	start_rev = pysvn.Revision(pysvn.opt_revision_kind.date, args.startdate)
	
	c = pysvn.Client()
	msgs = c.log(args.repo, revision_start=start_rev, revision_end=end_rev, discover_changed_paths=True)
	msgs.reverse() 
	for m in msgs:
		date = m.data['revprops']['svn:date']
		message = m.data['message'].strip()
		paths = []
	
		print "Date:\t\t", date
		print "Log Message:\t", message
		
		if len(m.data['changed_paths']) > 0: paths.append(m.data['changed_paths'][0].path) 
		for p in m.data['changed_paths'][1:]:
			paths.append(p.path)
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