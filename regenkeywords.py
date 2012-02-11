#!/usr/bin/python

import MySQLdb, argparse, datetime, unicodedata

from common import *
from config import Config
from database import DB
from databaseQueries import DBQ
from repo import Repo
from commit import Commit
from keywordsfilter import *

def regen(keywords):
    commits= DBQ.findByKeywords(keywords)

    for c in commits:
        diffs = c.getChangedTexts(c.getChangedTextMetadata())
        c.dbkeywords = c.getSynonyms(diffs)
        c.save()

        sys.stdout.write(".")
        sys.stdout.flush()
    print ""

if __name__ == "__main__":
    if sys.argv:
        regen(" ".join(sys.argv[1:]))
    else:
        regen('')

        
