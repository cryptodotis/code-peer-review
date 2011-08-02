#/usr/bin/python

import MySQLdb
from database import DB

map = None

def getMap():
    global map
    if map == None:
        conn = DB.getConn()
        c = conn.cursor()

        c.execute("SELECT * FROM " + DB.keyword._table)
        rows = c.fetchall()
        
        map = {}

        for r in rows:
            if not r[DB.keyword.keyword] in map:
                map[r[DB.keyword.keyword]] = []
                if r[DB.keyword.parent]:
                    map[r[DB.keyword.keyword]].append(r[DB.keyword.parent])

            elif r[DB.keyword.parent]:
                map[r[DB.keyword.keyword]].append(r[DB.keyword.parent])
    
    return map
