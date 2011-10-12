#!/usr/bin/python

import sys
import ply.yacc as yacc
import ply.lex as lex

import synonymmapping

# Lex =================================================================
reserved = {
    'and' : 'AND',
    'or' : 'OR'
    }
tokens = [
    'NAME',
    'LPAREN','RPAREN',
    ] + list(reserved.values())
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

def t_NAME(t):
     r'[-_a-zA-Z0-9_]+'
     t.type = reserved.get(t.value, 'NAME')
     return t

t_ignore = " \t\n"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Structure ===========================================================
class Tree:
	left = None
	right = None
	def __init__(self, l, r):
		self.left = l
		self.right = r
	def __repr__(self):
		s = "(" + repr(self.left) + " " + self.mode + " " + repr(self.right) + ")"
		return s
	def _getSQLNode(self, node, keywordcolumn, projectcolumn, maturitycolumn):
		sql = ""
		components = []
		if isinstance(node, str) or isinstance(node, unicode):
			if node.startswith("project-"):
				sql += " " + projectcolumn + " = %s"
				components.append(node.replace('project-', ''))
			elif node.startswith("maturity-"):
				sql += " " + maturitycolumn + " = %s"
				components.append(node.replace('maturity-', ''))
			else:
				sql += " " + keywordcolumn + " = %s"
				components.append(node)		
		else:
			innersql, newcomponents = node.getWhereClause(keywordcolumn, projectcolumn, maturitycolumn)

			#Don't have a ton of extra parens
			if len(newcomponents) > 1:			
				sql += "(" + innersql + ")"
			else:
				sql += innersql
				
			components.extend(newcomponents)
		return sql, components
	def getWhereClause(self, keywordcolumn, projectcolumn, maturitycolumn):

		sql, components = self._getSQLNode(self.left, keywordcolumn, projectcolumn, maturitycolumn)
		#We overload the AndTree to handle the single-node case
		if self.right:
			sql += " " + self.mode + " "

			nextsql, newcomponents = self._getSQLNode(self.right, keywordcolumn, projectcolumn, maturitycolumn)
			sql += nextsql
			components.extend(newcomponents)
		return sql, components
class AndTree(Tree):
	mode = "and"
class OrTree(Tree):
	mode = "or"


# Yacc ================================================================

#expression : NAME
#   | expression AND expression
#   | expression expression
#   | expression OR expression
#   | ( expression )

def p_expression_name(p):
    'expression : NAME'
    p[0] = AndTree(p[1], None)

def p_expression_names(p):
    'expression : expression expression'
    p[0] = AndTree(p[1], p[2])

def p_expression_and(p):
    'expression : expression AND expression'
    p[0] = AndTree(p[1], p[3])

def p_expression_or(p):
    'expression : expression OR expression'
    p[0] = OrTree(p[1], p[3])

def p_expression_parens(p):
    'expression : LPAREN expression RPAREN'
    p[0] = AndTree(p[2], None)

def p_error(p):
    print "Syntax error in input!"

lex.lex()
yacc.yacc()

# Interface ===========================================================

class KeywordsParser:
	@staticmethod
	def _isBalanced(keywords):
		balancedParens = 0
		for c in keywords:
			if c == "(":
				balancedParens += 1
			elif c == ")":
				balancedParens -= 1
			if balancedParens < 0:
				return False
		return balancedParens == 0
	@staticmethod
	def _trimnonsense(tokens): #get rid of beginning or ending combining words, including inside parens
		if tokens and tokens[0] in ["and", "or"]:
			tokens.pop(0)
		if tokens and tokens[-1] in ["and", "or"]:
			tokens.pop()
		for i in range(len(tokens) - 1):
			thistoken = tokens[i]
			nexttoken = tokens[i+1]
			if thistoken == "(": 
				if nexttoken in ["and", "or"]:
					tokens.pop(i+1)
					return KeywordsParser._trimnonsense(tokens)
		return tokens
	@staticmethod
	def _combinenonsense(tokens): #collapse repeated combining words e.g.  'tag1 and and tag2'
		if len(tokens) > 1:
			for i in range(len(tokens)-1): #remove successive combination words
				thistoken = tokens[i]
				nexttoken = tokens[i+1]
				if thistoken in ["and", "or"]:
					if nexttoken in ["and", "or"]:
						tokens.pop(i+1)
						return KeywordsParser._combinenonsense(tokens)
			for i in range(len(tokens)-1): #remove empty parens
				thistoken = tokens[i]
				nexttoken = tokens[i+1]
				if thistoken == "(" and nexttoken == ")": 
					tokens.pop(i)
					tokens.pop(i)
					return KeywordsParser._combinenonsense(tokens)
		return tokens
	@staticmethod
	def _preProcess(keywords):
		if not KeywordsParser._isBalanced(keywords):
			keywords = keywords.replace("(", "").replace(")", "")
		else:
			keywords = keywords.replace("(", " ( ").replace(")", " ) ")
		tokens = keywords.lower().split()
		tokens = KeywordsParser._combinenonsense(tokens)
		tokens = KeywordsParser._trimnonsense(tokens)
		tokens = KeywordsParser._combinenonsense(tokens)
		
		map = synonymmapping.getMap()
		for i in range(len(tokens)):
			if 'project-' + tokens[i] in map:
				tokens[i] = 'project-' + tokens[i]

		return ' '.join(tokens)   

	def __init__(self, keywords):
		self.keywords = KeywordsParser._preProcess(keywords)
		if self.keywords:
			self.result = yacc.parse(self.keywords)
		else:
			self.result = False

	def getWhereClause(self, keywordcolumn, projectcolumn, maturitycolumn):
		if self.result:
			return self.result.getWhereClause(keywordcolumn, projectcolumn, maturitycolumn)
		else:
			return ('', [])

if __name__ == "__main__":

	testcases = [
			"tag1  "
			,"and  "
			,"tag1   phantom"
			,"tag1   and   phantom"
			,"tag1   or   tag2"
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
			,")tag1(  "
			,"(and)  "
			,"((tag1)   phantom)"
			,"(tag1   and   phantom)"
			,"(((tag1   or   tag2)))"
			,"(tag1 phantom) maturity-tag3"
			,"(tag1 and and phantom) maturity-tag3"
			,"tag1 (phantom and and maturity-tag3)"
			,"(tag1 phantom) and and maturity-tag3 and and"
			,"and and (tag1 phantom) and and maturity-tag3 and and"
			,"(tag1 phantom) and maturity-tag3"
			,"(())()()()(())tag1 and phantom maturity-tag3"
			,"(tag1 and phantom) or maturity-tag3"
			,"tag1 and (phantom or maturity-tag3)"
			,"(tag1 or phantom) and maturity-tag3"
			,"tag1 or (phantom and maturity-tag3)"
			,"(tag1 and phantom) or (maturity-tag3 and tag4)"
			,"tag1 and (phantom or maturity-tag3) and tag4"
			,"tag1 and (phantom or maturity-tag3 and tag4)"
			,"(tag1 and phantom or maturity-tag3) and tag4"
			,"(tag1 and (phantom or maturity-tag3)) and tag4"
			,"tag1 and ((phantom or maturity-tag3) and tag4)"
			]


	for t in testcases:
		tree = KeywordsParser(t)
		print t
		print "\t", tree.getWhereClause("ck.keyword", "c.projecttag", "c.maturitytag")
		print ""
