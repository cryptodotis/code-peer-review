#!/usr/bin/python

import time, os, urlparse, re, datetime, synonymmapping

def fla(a, b):
	if a and not b:
		return a
	elif b and not a:
		return b
	else:
		a.extend(b)
		return a

def unixToGitDateFormat(t):
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def unixToDatetime(t):
	return datetime.datetime.utcfromtimestamp(t)

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
		
	if start and not end:
		end = time.time()
		start = end + int(start)
	elif end < start:
		end += start
		start = end - start
		end = end - start
	return start, end
