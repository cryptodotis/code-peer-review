#/usr/bin/python

import MySQLdb

from config import Config


map = None

def getMap():
    global map
    if map == None:
        conn = MySQLdb.connect (host = Config.host,
                                user = Config.username,
                                passwd = Config.password,
                                db = Config.database)
        c = conn.cursor()

        c.execute("SELECT * FROM keyword_tbl")
        rows = c.fetchall()
        
        map = {}

        for r in rows:
            if not r[0] in map:
                map[r[0]] = []
                if r[1]:
                    map[r[0]].append(r[1])
            elif r[1]:
                map[r[0]].append(r[1])
    
    return map
