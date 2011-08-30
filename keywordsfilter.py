#!/usr/bin/python

import sys

class Tree:
	mode = "INVALID"
	def __init__(self, n=""):
		if not n:
			self.nodes = []
		elif type(n) is str:
			self.nodes = [n]
		else:
			self.nodes = n
	def add(self, n):
		self.nodes.append(n)
	def appendToTail(self, n):
		self.nodes[len(self.nodes)-1].add(n)
	def getWhereClause(self, column, starting=False):
		sql = ""
		components = []
		for n in self.nodes:
			if type(n) is str:
				if starting:
					sql += " " + column + " = %s"
				else:
					sql += " " + self.mode + " " + column + " = %s"
				components.append(n)
			else:
				innersql, newcomponents = n.getWhereClause(column, True)
				if starting:
					sql += " (" + innersql + ")"
				else:
					sql += " " + self.mode + " (" + innersql + ")"
				components.extend(newcomponents)
			starting = False
		return sql, components
	def __repr__(self):
		s = "("
		for n in self.nodes:
			s += n.__repr__() + " " + self.mode  + " "
		s = s[:-(2+len(self.mode))]
		s += ")"
		return s

class AndTree(Tree):
	mode = "AND"
			
class OrTree(Tree):
	mode = "OR"
			
class KeywordsParser:
	@staticmethod
	def _trimnonsense(tokens):
		if len(tokens) and (tokens[0] == "and" or tokens[0] == "or"):
			tokens.pop(0)
		if len(tokens) and (tokens[len(tokens)-1] == "and" or tokens[len(tokens)-1] == "or"):
			tokens.pop(len(tokens)-1)
		return tokens
	@staticmethod
	def _combinenonsense(tokens):
		if len(tokens) > 1:
			for i in range(len(tokens)-1):
				thistoken = tokens[i]
				nexttoken = tokens[i+1]
				if thistoken == "and" or thistoken == "or":
					if nexttoken == "and" or nexttoken == "or":
						tokens.pop(i+1)
						return KeywordsParser._combinenonsense(tokens)
		return tokens
					
	def __init__(self, keywords):
		tokens = keywords.lower().split(' ')
		self.base = AndTree()
		
		tokens = KeywordsParser._combinenonsense(tokens)
		tokens = KeywordsParser._trimnonsense(tokens)
		
		if not len(tokens):
			return
		
		i=0
		while i < len(tokens):
			t = tokens[i]
			if i < len(tokens)-1:
				nextToken = tokens[i+1]
			else:
				nextToken = ""
			
			if t == "and":
				pass
			elif t == "or":
				self.base.appendToTail(nextToken)
				i += 1 # skip past next token
			elif nextToken == "and":
				self.base.add(t)
				i += 1 #skip past add
			elif nextToken == "or":
				n = OrTree(t)
				i += 2 #skip past or and go to next tag
				n.add(tokens[i])
				
				self.base.add(n)
			else:
				self.base.add(t)
			i += 1
	def getWhereClause(self, column):
		sql, components = self.base.getWhereClause(column, True)
		return (sql + " ", components)
	def __repr__(self):
		return self.base.__repr__()

if __name__ == "__main__":

	testcases = [
	"tag1"
	,"and"
	,"tag1 tag2"
	,"tag1 and tag2"
	,"tag1 or tag2"
	,"tag1 tag2 tag3"
	,"tag1 and and tag2 tag3"
	,"tag1 tag2 and and tag3"
	,"tag1 tag2 and and tag3 and and"
	,"and and tag1 tag2 and and tag3 and and"
	,"tag1 tag2 and tag3"
	,"tag1 and tag2 tag3"
	,"tag1 and tag2 or tag3"
	,"or"
	,"tag1 tag2"
	,"tag1 or tag2"
	,"tag1 or tag2"
	,"tag1 tag2 tag3"
	,"tag1 or or tag2 tag3"
	,"tag1 tag2 or or tag3"
	,"tag1 tag2 or or tag3 or or"
	,"or or tag1 tag2 or or tag3 or or"
	,"tag1 tag2 or tag3"
	,"tag1 or tag2 tag3"
	,"tag1 or tag2 or tag3"
	,"tag1 and tag2 or tag3 and tag4"
	]
		
	for t in testcases:
		tree = KeywordsParser(t)
		print t, "|", tree.getWhereClause("ck.keyword")