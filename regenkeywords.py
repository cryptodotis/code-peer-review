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
        sys.stdout.write("(" + str(c.repo.id) + ":" + c.uniqueid + ":")
        sys.stdout.flush()

        diffs = c.getChangedTexts(c.getChangedTextMetadata())
        sys.stdout.write("1")
        sys.stdout.flush()

        c.dbkeywords = c.getSynonyms(diffs)
        sys.stdout.write("2")
        sys.stdout.flush()

        c.save()
        sys.stdout.write("3)")
        sys.stdout.flush()
    print ""

if __name__ == "__main__":
    if sys.argv:
        regen(" ".join(sys.argv[1:]))
    else:
        regen('')

        
