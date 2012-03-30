#!/usr/bin/python

import sys, re
import ply.yacc as yacc
import ply.lex as lex

import synonymmapping
from database import DB

# Lex =================================================================
reserved = {
    'and' : 'AND',
    'or' : 'OR'
    }
tokens = [
    'NAME', 'MULTINAME',
    'LPAREN','RPAREN'
    ] + list(reserved.values())
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

#Be very, VERY careful about adding symbols to these regexes.
# Adding a single or double quote could allow arbitrary code execution thanks to a eval function
# Any changes must also be made to regex in setup and the regex in _stripIllegalCharacters
def t_MULTINAME(t):
     r'"[-_a-zA-Z0-9./]+ [-_a-zA-Z0-9./ ]+"'
     t.type = reserved.get(t.value, 'MULTINAME')
     return t
     
def t_NAME(t):
     r'"?[-_a-zA-Z0-9./]+"?'
     t.type = reserved.get(t.value, 'NAME')
     return t

t_ignore = " \t\n"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Structure ===========================================================
class Tree:
    left = None
    leftType = 'keyword'
    right = None
    rightType = 'keyword'
    
    _keywordphrase = "(SELECT ck.keyword FROM "+ DB.commitkeyword._table +" as ck WHERE ck.commitid = c.id)"
    _fulltextphrase_sql = "(SELECT wm.word FROM "+ DB.commitwordmap._table +" as wm WHERE wm.commitid = c.id)"
    _fulltextphrase_eval = "c.testFulltext('%s')"
    _projectphrase = "r.tagname"
    _maturityphrase = "r.maturity"
    
    def __init__(self, l, r):
        self.left = l
        self.right = r
        
        doLeft = doRight = False
        if isinstance(self.left, str) or isinstance(self.left, unicode):
            doLeft = True
            self.leftType = 'keyword'
        else:
            self.leftType = 'tree'
            
        if isinstance(self.right, str) or isinstance(self.right, unicode):
            doRight = True        
            self.rightType = 'keyword'            
        elif self.right is None:
            self.rightType = 'None'
        else:
            self.rightType = 'tree'
            
        if not (doLeft or doRight):
            return
            
        if doLeft: self.leftType = 'fulltext'
        if doRight: self.rightType = 'fulltext'
        for n in synonymmapping.getMap():
            if doLeft and n.__str__() == self.left:
                self.leftType = 'keyword'
            if doRight and n.__str__() == self.right:
                self.rightType = 'keyword'
    def __repr__(self):
        s = "(" + repr(self.left) + " " + self.mode + " " + repr(self.right) + ")"
        return s
    def _getEvalNode(self, type, node, nodeType):
        evalstring = ""
        components = []
        if nodeType == 'keyword':
            if node.startswith("project-"):
                if type == 'sql':       evalstring += " " + self._projectphrase + " = %s"
                elif type == 'eval':    evalstring += " " + self._projectphrase + " == '%s'"
                components.append(node.replace('project-', ''))
            elif node.startswith("maturity-"):
                if type == 'sql':       evalstring += " " + self._maturityphrase + " = %s"
                elif type == 'eval':    evalstring += " " + self._maturityphrase + " == '%s'"
                components.append(node.replace('maturity-', ''))
            else:
                if type == 'sql':       evalstring += "%s IN " + self._keywordphrase
                elif type == 'eval':    evalstring += "'%s' in " + self._keywordphrase
                components.append(node)		
        elif nodeType == 'fulltext':
            if type == 'sql':       evalstring += "%s IN " + self._fulltextphrase_sql
            elif type == 'eval':    evalstring += self._fulltextphrase_eval
            components.append(node)
        else:
            innersql, newcomponents = node.getEvaluationString(type)

            if node.right: evalstring += "(" + innersql + ")"
            else:          evalstring += innersql
                
            components.extend(newcomponents)
        return evalstring, components
    def anyTree(self):
        if self.leftType == 'tree':
            return True
        if self.rightType == 'tree':
            return True
        return False
    def anyFulltext(self):
        if self.leftType == 'fulltext':
            return True
        if self.rightType == 'fulltext':
            return True
        if self.leftType == 'tree':
            if self.left.anyFulltext(): return True
        if self.rightType == 'tree':
            if self.right.anyFulltext(): return True
           
        return False
    def getEvaluationString(self, type):

        evalstring, components = self._getEvalNode(type, self.left, self.leftType)
        #We overload the AndTree to handle the single-node case
        if self.right:
            evalstring += " " + self.mode + " "

            nextsql, newcomponents = self._getEvalNode(type, self.right, self.rightType)
            evalstring += nextsql
            components.extend(newcomponents)
        return evalstring, components
    def printTree(self, indent):
        if not self.right:
            if self.leftType == 'tree':
                self.left.printTree(indent)
            else:
                print indent + self.left
        else:
            print indent + self.mode
            if self.leftType == 'tree':
                self.left.printTree(indent + "\t")
            else:
                print indent + self.left
            if self.rightType == 'tree':
                self.right.printTree(indent + "\t")
            else:
                print indent + self.right
class AndTree(Tree):
    mode = "and"
class OrTree(Tree):
    mode = "or"


# Yacc ================================================================

def p_expression_name(p):
    '''expression : NAME 
                  | MULTINAME'''
    p[0] = AndTree(p[1].replace('"', ''), None)
    
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
    print "Syntax error in input: " + str(p) + "!"

lex.lex()
yacc.yacc()

# Interface ===========================================================
unallowed_characters = re.compile('[^-_a-zA-Z0-9./ ()]')

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
    def _combinenonsense(tokens): #collapse repeated combining words e.g.  'slackware and and sha256'
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
    def _stripIllegalCharacters(tokens): #Violently remove characters not permitted by t_NAME regex
        tokens = unallowed_characters.sub('', tokens)
        return tokens
    @staticmethod
    def _preProcess(keywords):
        if not KeywordsParser._isBalanced(keywords):
            keywords = keywords.replace("(", "").replace(")", "")
        else:
            keywords = keywords.replace("(", " ( ").replace(")", " ) ")
        keywords = KeywordsParser._stripIllegalCharacters(keywords)
        tokens = keywords.lower().split()
        tokens = KeywordsParser._combinenonsense(tokens)
        tokens = KeywordsParser._trimnonsense(tokens)
        tokens = KeywordsParser._combinenonsense(tokens)
        
        tokens = synonymmapping.projectizeTags(tokens)

        return ' '.join(tokens)   

    def __init__(self, keywords):
        self.keywords = KeywordsParser._preProcess(keywords)
        if self.keywords:
            self.result = yacc.parse(self.keywords)
        else:
            self.result = False

    def getEvaluationString(self, type):
        if self.result:
            return self.result.getEvaluationString(type)
        else:
            return ('', [])
    def anyFulltext(self):
        return self.result.anyFulltext()
    def dump(self):
        if self.result:
            evalstr, evalcomponents = self.result.getEvaluationString('eval')
            print "\t", evalstr % tuple(evalcomponents)
            
            evalstr, evalcomponents = self.result.getEvaluationString('sql')
            print "\t", evalstr, evalcomponents
            
            #self.result.printTree("\t")
        else:
            print ""

if __name__ == "__main__":

    testcases = [
            "slackware  "
            , "tag1  "
            , "\"slackware\"  "
            ,"and  "
            ,"slackware   testcases-git"
            ,"slackware or (tag1 and doxygen)"
            ,"slackware   and   testcases-git"
            ,"slackware   or   sha256"
            ,"slackware testcases-git maturity-suse"
            ,'"slackware testcases-git" maturity-suse'
            ,"slackware and and testcases-git maturity-suse"
            ,"slackware testcases-git and and maturity-suse"
            ,"slackware testcases-git and and maturity-suse and and"
            ,"and and slackware testcases-git and and maturity-suse and and"
            ,"slackware testcases-git and maturity-suse"
            ,"slackware and testcases-git maturity-suse"
            ,"slackware and testcases-git or maturity-suse"
            ,"or"
            ,"slackware testcases-git"
            ,"slackware or testcases-git"
            ,"slackware or testcases-git"
            ,"slackware testcases-git maturity-suse"
            ,"slackware or or testcases-git maturity-suse"
            ,"slackware testcases-git or or maturity-suse"
            ,"slackware testcases-git or or maturity-suse or or"
            ,"or or slackware testcases-git or or maturity-suse or or"
            ,"slackware testcases-git or maturity-suse"
            ,"slackware or testcases-git maturity-suse"
            ,"slackware or testcases-git or maturity-suse"
            ,"slackware and testcases-git or maturity-suse and tag4"
            ,")slackware(  "
            ,"(and)  "
            ,"((slackware)   testcases-git)"
            ,"(slackware   and   testcases-git)"
            ,"(((slackware   or   sha256)))"
            ,"(slackware testcases-git) maturity-suse"
            ,"(slackware and and testcases-git) maturity-suse"
            ,"slackware (testcases-git and and maturity-suse)"
            ,"(slackware testcases-git) and and maturity-suse and and"
            ,"and and (slackware testcases-git) and and maturity-suse and and"
            ,"(slackware testcases-git) and maturity-suse"
            ,"(())()()()(())slackware and testcases-git maturity-suse"
            ,"(slackware and testcases-git) or maturity-suse"
            ,"slackware and (testcases-git or maturity-suse)"
            ,"(slackware or testcases-git) and maturity-suse"
            ,"slackware or (testcases-git and maturity-suse)"
            ,"(slackware and testcases-git) or (maturity-suse and tag4)"
            ,"slackware and (testcases-git or maturity-suse) and tag4"
            ,"slackware and (testcases-git or maturity-suse and tag4)"
            ,"(slackware and testcases-git or maturity-suse) and tag4"
            ,"(slackware and (testcases-git or maturity-suse)) and tag4"
            ,"slackware and ((testcases-git or maturity-suse) and tag4)"
            
            ,"tag1"
            ,"tag1' x"
            ,"tag1' or 1==1 '"
            ]


    for t in testcases:
        tree = KeywordsParser(t)
        print t
        tree.dump()
        print ""
