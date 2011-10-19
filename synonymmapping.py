#!/usr/bin/python

import MySQLdb, pygraph.classes.digraph
from common import *
from database import DB

map = None

class KeywordType:
	STANDARD = 1
	#standard keywords can appear in a commit message, filename/path, or the diffed code.  
	APICALL = 2
	#api keywords can appear in a commit message or diffed code, and represent an API call to a library
	# the individual tag does not apply, only the parent tag
	MAPPING = 3
	#mapping keywords will not appear anywhere in the log, diff, or pathname, but are used to apply tags and apply a parent tag

def getMap():
	global map
	if not map:
		conn = DB.getConn()
		c = conn.cursor()

		c.execute("SELECT * FROM " + DB.keyword._table)
		rows = c.fetchall()

		map = pygraph.classes.digraph.digraph()

		for r in rows:
			keyword = r[DB.keyword.keyword]
			keyword_regex = re.compile('(?<=[^a-zA-Z])' + keyword + '(?![a-zA-Z])') # k is not surrounded by alpha characters.  
			parent = r[DB.keyword.parent]
			parent_regex = '' if not parent else re.compile('(?<=[^a-zA-Z])' + parent + '(?![a-zA-Z])') 
			type = r[DB.keyword.type]

			if not map.has_node(keyword):
				map.add_node(keyword, [('type', type), ('regex', keyword_regex)])
			else:
				pass #We take the first type defined, on the assumption that an APICALL will not also be something else
				#	And that a MAPPING will not also be standard

			if parent and not map.has_node(parent):
				map.add_node(parent, [('type', KeywordType.STANDARD), ('regex', parent_regex)])
				#We define a parent tag as being standard. Really it should be max(existing, type) but that requires a logical definition of 
				# increasing values of type - which we don't do
			if parent:
				map.add_edge((keyword, parent), label=type)

		c.execute("SELECT tagname FROM " + DB.repo._table)
		rows = c.fetchall()
		for r in rows:
			keyword = r[0]
			keyword_regex = re.compile('(?<=[^a-zA-Z])' + keyword + '(?![a-zA-Z])') 
			parent = 'project-' + r[0]
			parent_regex = re.compile('(?<=[^a-zA-Z])' + parent + '(?![a-zA-Z])') 
			type = KeywordType.APICALL #apply only the project tag, not the non-project tag
			
			if not map.has_node(keyword):
				map.add_node(keyword, [('type', type), ('regex', keyword_regex)])
			if not map.has_node(parent):
				map.add_node(parent, [('type', KeywordType.STANDARD), ('regex', parent_regex)])
    			map.add_edge((keyword, parent), label=type)
    	return map

def getAllChildTags(map, node, sofar=None):
	keywords = set() if not sofar else sofar
	for e in map.neighbors(node):
		#This could potentially apply an APICALL tag, but for that to happen
		# an APICALL tag would have to be a child of another.  This shouldn't happen
		# so we apply all parent tags always.
		if e not in keywords:
			keywords.add(e)
			keywords = keywords.union(getAllChildTags(map, e, keywords))
	return keywords
		

def getTags(commit):
	log = commit.message.lower()
	paths = []
	for i in range(len(commit.files)): paths.append(commit.files[i].lower())

	map = getMap()
	keywords = set()
	for k in map.nodes():
		k_type = map.node_attributes(k)[0][1]
		kregex = map.node_attributes(k)[1][1]

		#Don't look for mapping keywords anywhere, they'll be applied by graph travel from another keyword
		if k_type == KeywordType.MAPPING:
			continue

		if kregex.search(log):
			#Do not apply the base tag for KeywordType.APICALL			
			if k_type != KeywordType.APICALL:
				keywords.add(k)

			#Apply all children tags				
			keywords = keywords.union(getAllChildTags(map, k))
		
		#Do not do path search for APICALL keywords
		if k_type == KeywordType.APICALL:
			continue
		
		for p in paths:
			if kregex.search(p):
				#Do not apply the base tag for KeywordType.APICALL			
				if k_type != KeywordType.APICALL:
					keywords.add(k)
				keywords = keywords.union(getAllChildTags(map, k))
	return keywords

	
def projectizeTags(tokens):
	map = getMap()
	for i in range(len(tokens)):
		if map.has_node('project-' + tokens[i]):
			tokens[i] = 'project-' + tokens[i]
	return tokens

if __name__ == "__main__":
	map = getMap()
	for n in map.nodes():
		print n
		print "\t", map.neighbors(n)
