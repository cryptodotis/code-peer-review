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
		
	def pprint(self):
		s = "(" + str(self.id) + ", "
		
		for i in dir(Repo.Type):
			if self.type == getattr(Repo.Type, i):
				s += i
		
		s+= ", " + self.url + ")"
		print s
				
	class Type:
		SVN = 1
		GIT = 2
		CVS = 3
		RSS = 4
		EMAIL = 5