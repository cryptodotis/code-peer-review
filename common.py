#!/usr/bin/python

import time, os, urlparse, re, datetime

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
		
	if start < 0 and not end:
		end = time.time()
		start = end + int(start)
	elif end < start:
		tmp = end
		end = start
		start = tmp
	return start, end

class MicroMock(object):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
