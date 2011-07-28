#!/usr/bin/python

import MySQLdb, argparse
from config import Config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--wipe', dest='wipe', action='store_true', help='Instead of creating tables if they don\'t exist - empty the database.')
    parser.add_argument('--populate', dest='populate', action='store_true', help='If a reference data table is created, also populate it with some test data.  Mandatory refdata tables will be populated regardless.')
    args = parser.parse_args()
    


    conn = MySQLdb.connect (host = Config.host,
                            user = Config.username,
                            passwd = Config.password,
                            db = Config.database)

    c = conn.cursor()
    
    if args.wipe:
        try:
            c.execute("DROP TABLE repotype_tbl")
        except:
            pass
        try:
            c.execute("DROP TABLE repo_tbl")
        except:
            pass
        try:
            c.execute("DROP TABLE keyword_tbl")        
        except:
            pass
        try:
            c.execute("DROP TABLE commit_tbl")
        except:
            pass
        try:
            c.execute("DROP TABLE commitkeyword_tbl")
        except:
            pass
        try:
            c.execute("DROP TABLE commitfile_tbl")
        except:
            pass

    else:
        #repotype_tbl -------------------------------------------
        c.execute("SHOW TABLES LIKE 'repotype_tbl'")
        r = c.fetchone()
        if r:
            print "Repo Type Table Exists"
        else:
            print "Creating Repo Type Table..."
            repotype = """CREATE TABLE repotype_tbl
			(
			id smallint NOT NULL PRIMARY KEY,
			type varchar(10) NOT NULL UNIQUE
			) ENGINE=innodb;
			"""
            c.execute(repotype)
            
            print 'Populating Repo Type...'
            repotype = """INSERT INTO repotype_tbl (id, type)
			SELECT 1, 'svn' UNION
			SELECT 2, 'git' UNION
			SELECT 3, 'cvs' UNION
			SELECT 4, 'rss' UNION
			SELECT 5, 'email'
			"""
            c.execute(repotype)

        #repos_tbl ---------------------------------------------
        c.execute("SHOW TABLES LIKE 'repo_tbl'")
        r = c.fetchone()
        if r:
            print "Repo Table Exists"
        else:
            print "Creating Repos Table..."
            sql = """CREATE TABLE repo_tbl
			(
			id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
			repotypeid tinyint NOT NULL,
			url varchar(255) NOT NULL UNIQUE
			) ENGINE=innodb;
			"""
            c.execute(sql)
            
            if args.populate:
                print 'Populating Repos...'
        	sql = """INSERT INTO repo_tbl(repotypeid, url)
			SELECT 2, 'https://github.com/crooks/aam2mail.git' UNION
			SELECT 2, 'https://github.com/crooks/nymserv' UNION
			SELECT 1, 'https://svn.torproject.org/svn/'
			"""
                c.execute(sql)

        #keyword_tbl ---------------------------------------------
        c.execute("SHOW TABLES LIKE 'keyword_tbl'")
        r = c.fetchone()
        if r:
            print "Keyword Table Exists"
        else:
            print "Creating Keyword Table..."
            sql = """CREATE TABLE keyword_tbl
			(
			keyword varchar(50) NOT NULL,
			parent varchar(50) 
			) ENGINE=innodb;
			"""
            c.execute(sql)
            
            if args.populate:
                print 'Populating Keywords...'
        	sql = """INSERT INTO keyword_tbl(keyword, parent)
			SELECT 'debian', NULL UNION
			SELECT 'oaep', 'crypto-padding' UNION
			SELECT 'oaep', 'asymmetric-crypto' UNION
			SELECT 'oaep', 'RSA' UNION
			SELECT 'vidalia', 'project-tor'
			"""
                c.execute(sql)

        #commit_tbl ----------------------------------------
        c.execute("SHOW TABLES LIKE 'commit_tbl'")
        r = c.fetchone()
        if r:
            print "Commit Table Exists"
        else:
            print "Creating Commit Table..."
            sql = """CREATE TABLE commit_tbl
                        (
                        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        repoid tinyint NOT NULL,
			date int NOT NULL,
                        message text 
                        ) ENGINE=innodb;
                        """
            c.execute(sql)
        #commitfile_tbl ----------------------------------------
        c.execute("SHOW TABLES LIKE 'commitfile_tbl'")
        r = c.fetchone()
        if r:
            print "Commit File Table Exists"
        else:
            print "Creating Commit Table..."
            sql = """CREATE TABLE commitfile_tbl
                        (
                        commitid int NOT NULL,
			file varchar(512)
                        ) ENGINE=innodb;
                        """
            c.execute(sql)
        #commitkeyword_tbl ----------------------------------------
        c.execute("SHOW TABLES LIKE 'commitkeyword_tbl'")
        r = c.fetchone()
        if r:
            print "Commit Keyword Table Exists"
        else:
            print "Creating Commit Keywords Table..."
            sql = """CREATE TABLE commitkeyword_tbl
                        (
                        commitid int NOT NULL,
                        keywordid int NOT NULL,
			PRIMARY KEY(commitid, keywordid)
                        ) ENGINE=innodb;
                        """
            c.execute(sql)


    conn.commit()
