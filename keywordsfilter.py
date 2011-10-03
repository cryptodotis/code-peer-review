#!/usr/bin/python

import sys

import synonymmapping

class Tree:
	mode = "INVALID"
	def __init__(self, n=""):
		if not n:
			self.nodes = []
		elif isinstance(n, str):
			self.nodes = [n]
		else:
			self.nodes = n
	def add(self, n):
		self.nodes.append(n)
	def appendToTail(self, n):
		self.nodes[-1].add(n)
	def getWhereClause(self, keywordcolumn, projectcolumn, maturitycolumn, starting=False):
		sql = ""
		components = []
		for n in self.nodes:
			if isinstance(n, str):
				if not starting:
					sql += " " + self.mode

				if n.startswith("project-"):
					sql += " " + projectcolumn + " = %s"
					components.append(n.replace('project-', ''))
				elif n.startswith("maturity-"):
					sql += " " + maturitycolumn + " = %s"
					components.append(n.replace('maturity-', ''))
				else:
					sql += " " + keywordcolumn + " = %s"
					components.append(n)
			else:
				innersql, newcomponents = n.getWhereClause(keywordcolumn, projectcolumn, maturitycolumn, True)
				if starting:
					sql += " (" + innersql + ")"
				else:
					sql += " " + self.mode + " (" + innersql + ")"
				components.extend(newcomponents)
			starting = False
		return sql, components
	def __repr__(self):
		s = "("
		tmp = [repr(n) for n in self.nodes]
		joiner = " " + self.mode + " "
		s += joiner.join(tmp)
		s = s[:-(2+len(self.mode))] + ")"
		return s

class AndTree(Tree):
	mode = "AND"

class OrTree(Tree):
	mode = "OR"

class KeywordsParser:
	@staticmethod
	def _trimnonsense(tokens):
		if tokens and tokens[0] in ["and", "or"]:
			tokens.pop(0)
		if tokens and tokens[-1] in ["and", "or"]:
			tokens.pop()
		return tokens
	@staticmethod
	def _combinenonsense(tokens):
		if len(tokens) > 1:
			for i in range(len(tokens)-1):
				thistoken = tokens[i]
				nexttoken = tokens[i+1]
				if thistoken in ["and", "or"]:
					if nexttoken in ["and", "or"]:
						tokens.pop(i+1)
						return KeywordsParser._combinenonsense(tokens)
		return tokens

	base = AndTree()
	projecttokens = []
	maturitytokens = []
	tokens = []
	def __init__(self, keywords):
		self.tokens = keywords.lower().split(' ')
		self.base = AndTree()

		self.tokens = KeywordsParser._combinenonsense(self.tokens)
		self.tokens = KeywordsParser._trimnonsense(self.tokens)

		map = synonymmapping.getMap()

		if not self.tokens:
			return

		i = 0
		while i < len(self.tokens):
			t = self.tokens[i]
			if i < len(self.tokens)-1:
				nextToken = self.tokens[i+1]
			else:
				nextToken = ""

			if t not in ['and', 'or'] and 'project-' + t in map:
				t = 'project-' + t

			if t == "or":
				self.base.appendToTail(nextToken)
				i += 1 # skip past next token
			elif t == "and":
				pass
			elif nextToken == "and":
				self.base.add(t)
				i += 1 #skip past add
			elif nextToken == "or":
				n = OrTree(t)
				i += 2 #skip past or and go to next tag
				n.add(self.tokens[i])

				self.base.add(n)
			else:
				self.base.add(t)
			i += 1
	def getWhereClause(self, keywordcolumn, projectcolumn, maturitycolumn):
		sql, components = self.base.getWhereClause(keywordcolumn, projectcolumn, maturitycolumn, True)
		sql += " "

		return (sql, components)
	def __repr__(self):
		return repr(self.base)

if __name__ == "__main__":

	testcases = [
			"tag1"
			,"and"
			,"tag1 phantom"
			,"tag1 and phantom"
			,"tag1 or tag2"
			,"tag1 phantom maturity-tag3"
			,"tag1 and and phantom maturity-tag3"
			,"tag1 phantom and and maturity-tag3"
			,"tag1 phantom and and maturity-tag3 and and"
			,"and and tag1 phantom and and maturity-tag3 and and"
			,"tag1 phantom and maturity-tag3"
			,"tag1 and phantom maturity-tag3"
			,"tag1 and phantom or maturity-tag3"
			,"or"
			,"tag1 phantom"
			,"tag1 or phantom"
			,"tag1 or phantom"
			,"tag1 phantom maturity-tag3"
			,"tag1 or or phantom maturity-tag3"
			,"tag1 phantom or or maturity-tag3"
			,"tag1 phantom or or maturity-tag3 or or"
			,"or or tag1 phantom or or maturity-tag3 or or"
			,"tag1 phantom or maturity-tag3"
			,"tag1 or phantom maturity-tag3"
			,"tag1 or phantom or maturity-tag3"
			,"tag1 and phantom or maturity-tag3 and tag4"
			]

	for t in testcases:
		tree = KeywordsParser(t)
		print t, "|", tree.getWhereClause("ck.keyword", "c.projecttag", "c.maturitytag")
