#!/usr/bin/python
import argparse, sys, time, os
import pysvn

from common import *
from commit import Commit

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
		message = m.data['message']
		paths = [p.path for p in m.data['changed_paths']]

		c = Commit(message, date, paths)
		c.save()
		c.pprint()
