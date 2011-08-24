#!/usr/bin/python

import time, MySQLdb

from database import DB

class Repo:
	id = 0
	type = 0
	url = ''
	def __init__(self, row):
		self.id = row[DB.repo.id]
		self.type = row[DB.repo.repotypeid]
		self.url = row[DB.repo.url]
		self.tagname = row[DB.repo.tagname]
		self.tagmaturity = row[DB.repo.tagmaturity]
		
	def pprint(self):
		s = "(" + str(self.id) + ", "
		
		for i in dir(Repo.Type):
			if self.type == getattr(Repo.Type, i):
				s += i
		
		s+= ", " + self.url + ", project-" + self.tagname + ", maturity-" + self.tagmaturity + ")"
		print s
				
	class Type:
		SVN = 1
		GIT = 2
		CVS = 3
		RSS = 4
		EMAIL = 5
		BAZAAR = 6
		MERCURIAL = 7
	
	#Maturity Values
	#	pervasive - project is used by hundreds or thousands of people who regurally rely on it for protection
	#	stable - project is in use and stable on public servers, but not pervasive
	#	beta - project can be used on public servers but is marked as beta by the authors
	#	development - project is in development
