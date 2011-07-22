#!/usr/bin/python
import argparse, sys, time, os
import pysvn

import synonymmapping

def getDate(s):
	try:
		i = int(s)
		return i
	except:
		return -1
	
def getSynonyms(log, paths):
	log = log.lower()
	for i in range(len(paths)):	paths[i] = paths[i].lower()
	
	keywords = set()
	for k in synonymmapping.map:
		if k in log:
			keywords.add(k)
			for v in synonymmapping.map[k]: keywords.add(v)
		for p in paths:
			if k in p:
				keywords.add(k)
				for v in synonymmapping.map[k]: keywords.add(v)
	
	return keywords
	
def getBasePath(paths):
	trunks = [p for p in paths if "/trunk" in p]
	branches = [p for p in paths if "/branches" in p]
	tags = [p for p in paths if "/tags" in p]
	odd = [p for p in paths if p not in trunks and p not in branches and p not in tags]
	if ((1 if len(trunks) > 0 else 0) + (1 if len(branches) > 0 else 0) + \
		(1 if len(tags) > 0 else 0) + (1 if len(odd) > 0 else 0)) > 1:
		ret = []
		if len(trunks) > 0: ret.append(os.path.commonprefix(trunks))
		if len(branches) > 0: ret.append(os.path.commonprefix(branches))
		if len(tags) > 0: ret.append(os.path.commonprefix(tags))
		if len(odd) > 0: ret.append(os.path.commonprefix(odd))
		return ret
	else:
		return os.path.dirname(os.path.commonprefix(paths))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Given a repo url, a startdate and enddate, process the commits between.')
	parser.add_argument('repo')
	parser.add_argument('startdate', type=getDate)
	parser.add_argument('enddate', type=getDate)
	args = parser.parse_args()
	
	try:
		int(args.enddate)
		int(args.startdate)
	except ValueError:
		print "Invalid Start or End Date"
		exit
	
	if args.enddate == 0 and args.startdate < 0:
		args.enddate = time.time()
		args.startdate = args.enddate + int(args.startdate)
	elif args.enddate < args.startdate:
		tmp = args.enddate
		args.enddate = args.startdate
		args.startdate = tmp
	
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