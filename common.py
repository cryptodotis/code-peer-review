#!/usr/bin/python

import time,os,urlparse,re, datetime

import synonymmapping

def unixToGitDateFormat(t):
	s = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
	return s

def urlToFolder(url):
	scheme, netloc, path, parameters, query, fragment = urlparse.urlparse(url)
	folder = netloc + path
	folder = folder.replace('/', '-')
	return folder

def fixDates(start, end):
	try:
		end = int(end)
		start = int(start)
	except ValueError:
		print "Invalid Start or End Date"
		exit
		
	if end == 0 and start < 0:
		end = time.time()
		start = end + int(start)
	elif end < start:
		tmp = end
		end = start
		start = tmp
	return start, end
