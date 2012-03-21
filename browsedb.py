#!/usr/bin/python

import MySQLdb, argparse, datetime, unicodedata

from common import *
from config import Config
from database import DB
from databaseQueries import DBQ
from repo import Repo
from commit import Commit
from keywordsfilter import *

def browse(keywords):
    commits = DBQ.findByKeywordsAndFulltext(keywords)
    
    for c in commits:
        print "---------"
        c.pprint()

if __name__ == "__main__":
    if sys.argv:
        browse(" ".join(sys.argv[1:]))
    else:
        browse('')

        
        
