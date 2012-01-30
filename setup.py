#!/usr/bin/python

import MySQLdb, argparse, os
from database import DB


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--wipe', dest='wipe', action='store_true', help='Instead of creating tables if they don\'t exist - empty the database.')
    parser.add_argument('--populate', dest='populate', action='store_true', help='If a reference data table is created, also populate it with some test data.  Mandatory refdata tables will be populated regardless.')
    parser.add_argument('--testpopulate', dest='testpopulate', action='store_true', help='Only populate the testcases repo. Use with --populate')
    parser.add_argument('--keywords', dest='keywords', action='store_true', help='Only reprocess the kwywords table.')
    args = parser.parse_args()
    


    conn = DB.getConn()

    c = conn.cursor()
    
    if args.wipe:
        try:
            c.execute("DROP TABLE " + DB.repotype._table)
        except:
            pass
        try:
            c.execute("DROP TABLE " + DB.repo._table)
        except:
            pass
        try:
            c.execute("DROP TABLE " + DB.keyword._table)        
        except:
            pass
        try:
            c.execute("DROP TABLE " + DB.commit._table)
        except:
            pass
        try:
            c.execute("DROP TABLE " + DB.commitkeyword._table)
        except:
            pass
        try:
            c.execute("DROP TABLE " + DB.commitfile._table)
        except:
            pass

    else:
        #repotype._table + """ -------------------------------------------
        c.execute("SHOW TABLES LIKE '" + DB.repotype._table + "'")
        r = c.fetchone()
        if r:
            print "Repo Type Table Exists"
        else:
            print "Creating Repo Type Table..."
            repotype = "CREATE TABLE " + DB.repotype._table + """
                        (
                        id smallint NOT NULL PRIMARY KEY,
                        type varchar(10) NOT NULL UNIQUE
                        ) ENGINE=innodb;
                        """
            c.execute(repotype)
            
            print 'Populating Repo Type...'
            repotype = "INSERT INTO " + DB.repotype._table + """(id, type)
                        SELECT 1, 'svn' UNION
                        SELECT 2, 'git' UNION
                        SELECT 3, 'cvs' UNION
                        SELECT 4, 'rss' UNION
                        SELECT 5, 'email' UNION
                        SELECT 6, 'bazaar' UNION
                        SELECT 7, 'mercurial' UNION
                        SELECT 8, 'targz' UNION
                        SELECT 9, 'darcs'
                        """
            c.execute(repotype)

        #repos._table + """ ---------------------------------------------
        c.execute("SHOW TABLES LIKE '" + DB.repo._table + "'")
        r = c.fetchone()
        if r:
            print "Repo Table Exists"
        else:
            print "Creating Repos Table..."
            sql = "CREATE TABLE " + DB.repo._table + """
                    (
                    id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    repotypeid tinyint NOT NULL,
                    url varchar(255) NOT NULL UNIQUE,
                    viewlink varchar(512) NULL,
                    tagname varchar(30) NOT NULL,
                    maturity varchar(20) NOT NULL
                    ) ENGINE=innodb;
                    """
            c.execute(sql)
            
            if args.testpopulate:
                print 'Populating Repos...'
                sql = "INSERT INTO " + DB.repo._table + """(repotypeid, url, viewlink, tagname, maturity)
                SELECT 2, 'git://github.com/tomrittervg/Code-Audit-Feed-Test-Cases.git', 'https://github.com/tomrittervg/Code-Audit-Feed-Test-Cases/commit/%ID', 'testcases', 'development' UNION
                SELECT 1, 'http://code-audit-feed-testcases.googlecode.com/svn/trunk/', 'http://code.google.com/p/code-audit-feed-testcases/source/detail?r=%ID', 'testcases', 'development' """

                DB.execute(c, sql)
            elif args.populate:
                print 'Populating Repos...'
                sql = "INSERT INTO " + DB.repo._table + """(repotypeid, url, viewlink, tagname, maturity)
                SELECT 2, 'https://github.com/cryptodotis/crypto.is-docs', 'https://github.com/cryptodotis/crypto.is-docs/commit/%ID', 'crypto.is-docs', 'beta' UNION
                SELECT 2, 'https://github.com/moxie0/Convergence.git', 'https://github.com/moxie0/Convergence/commit/%ID', 'convergence', 'beta' UNION
                SELECT 2, 'https://github.com/brl/obfuscated-openssh', 'https://github.com/brl/obfuscated-openssh/commit/%ID', 'obfuscated-openssh', 'stable' UNION
                SELECT 1, 'http://phantom.googlecode.com/svn/trunk/', 	'http://code.google.com/p/phantom/source/detail?r=%ID', 'phantom', 'development' UNION
                SELECT 8, 'http://www.agroman.net/corkscrew/', 		NULL, 'corkscrew', 'development' UNION
                SELECT 9, 'http://tahoe-lafs.org/source/tahoe-lafs/trunk/', 'http://tahoe-lafs.org/trac/tahoe-lafs/changeset?old_path=%2Ftrunk&old=%ID&new_path=%2Ftrunk&new=%ID', 'tahoe-lafs', 'beta' UNION
                SELECT 2, 'git://briar.git.sourceforge.net/gitroot/briar/prototype', 'http://briar.git.sourceforge.net/git/gitweb.cgi?p=briar/prototype;a=commitdiff;h=%ID', 'briar', 'development' UNION
                SELECT 2, 'git://briar.git.sourceforge.net/gitroot/briar/docs', 'http://briar.git.sourceforge.net/git/gitweb.cgi?p=briar/docs;a=commitdiff;h=%ID', 'briar-docs', 'development' UNION
                SELECT 2, 'https://git.torproject.org/user/jvoisin/mat.git', 'https://gitweb.torproject.org/user/jvoisin/mat.git/commitdiff/%ID', 'mat', 'beta' UNION
                SELECT 2, 'https://github.com/secYOUre/Encounter.git', 'https://github.com/secYOUre/Encounter/commit/%ID', 'encounter', 'development' UNION
                SELECT 2, 'https://github.com/servalproject/batphone.git', 'https://github.com/servalproject/batphone/commit/%ID', 'serval', 'development' UNION
                SELECT 8, 'http://www.issihosts.com/haveged/', '', 'haveged', 'beta' UNION"""
                
                #tor
                sql += """
                SELECT 2, 'https://git.torproject.org/arm.git', 		'https://gitweb.torproject.org/arm.git/commitdiff/%ID', 'tor-arm', 			'stable' UNION
                SELECT 2, 'https://git.torproject.org/bridgedb.git', 		'https://gitweb.torproject.org/bridgedb.git/commitdiff/%ID', 'tor-bridgedb', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/debian/tor.git', 		'https://gitweb.torproject.org/debian/tor.git/commitdiff/%ID', 'tor-debian-tor', 	'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/flashproxy.git', 		'https://gitweb.torproject.org/flashproxy.git/commitdiff/%ID', 'tor-flashproxy', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/gettor.git', 		'https://gitweb.torproject.org/gettor.git/commitdiff/%ID', 'tor-gettor', 		'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/https-everywhere.git', 	'https://gitweb.torproject.org/https-everywhere.git/commitdiff/%ID', 'https-everywhere', 	'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/jtorctl.git', 		'https://gitweb.torproject.org/jtorctl.git/commitdiff/%ID', 'tor-jtorctl', 		'stable' UNION
                SELECT 2, 'https://git.torproject.org/metrics-db.git', 		'https://gitweb.torproject.org/metrics-db.git/commitdiff/%ID', 'tor-metrics-db', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/metrics-tasks.git', 	'https://gitweb.torproject.org/metrics-tasks.git/commitdiff/%ID', 'tor-metrics-tasks',	'stable' UNION
                SELECT 2, 'https://git.torproject.org/metrics-utils.git', 	'https://gitweb.torproject.org/metrics-utils.git/commitdiff/%ID', 'tor-metrics-utils', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/metrics-web.git', 	'https://gitweb.torproject.org/metrics-web.git/commitdiff/%ID', 'tor-metrics-web', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/obfsproxy.git', 		'https://gitweb.torproject.org/obfsproxy.git/commitdiff/%ID', 'tor-obfsproxy', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/orbot.git', 		'https://gitweb.torproject.org/orbot.git/commitdiff/%ID', 'tor-orbot', 		'stable' UNION
                SELECT 2, 'https://git.torproject.org/puppetor.git', 		'https://gitweb.torproject.org/puppetor.git/commitdiff/%ID', 'tor-puppetor', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/pytorctl.git', 		'https://gitweb.torproject.org/pytorctl.git/commitdiff/%ID', 'tor-pytorctl', 	'stable' UNION
                SELECT 2, 'https://git.torproject.org/thandy.git', 		'https://gitweb.torproject.org/thandy.git/commitdiff/%ID', 'tor-thandy', 		'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/tor.git', 		'https://gitweb.torproject.org/tor.git/commitdiff/%ID', 'tor', 			'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/torbutton.git', 		'https://gitweb.torproject.org/torbutton.git/commitdiff/%ID', 'torbutton', 		'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/tordnsel.git', 		'https://gitweb.torproject.org/tordnsel.git/commitdiff/%ID', 'tor-dnsel', 		'stable' UNION
                SELECT 2, 'https://git.torproject.org/torsocks.git', 		'https://gitweb.torproject.org/torsocks.git/commitdiff/%ID', 'torsocks', 		'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/torspec.git', 		'https://gitweb.torproject.org/torspec.git/commitdiff/%ID', 'torspec', 		'pervasive' UNION
                SELECT 2, 'https://git.torproject.org/vidalia.git', 		'https://gitweb.torproject.org/vidalia.git/commitdiff/%ID', 'vidalia', 		'pervasive' UNION"""
                #crypto libraries
                sql += """
                SELECT 2, 'git://git.gnupg.org/libgcrypt.git', 'http://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git;a=commitdiff;h=%ID', 'libgcrypt', 'pervasive' UNION"""
                #file crypto
                sql += """
                SELECT 2, 'git://git.gnupg.org/gnupg.git', 'http://git.gnupg.org/cgi-bin/gitweb.cgi?p=gnupg.git;a=commitdiff;h=%ID', 'gnupg', 'pervasive' UNION
                SELECT 2, 'https://github.com/dyne/Tomb.git', 'https://github.com/dyne/Tomb/commit/%ID', 'tomb', 'stable' UNION"""
                #remailer
                sql += """
                SELECT 2, 'https://github.com/crooks/aam2mail.git', 'https://github.com/crooks/aam2mail/commit/%ID', 'aam2mail', 'stable' UNION
                SELECT 2, 'https://github.com/crooks/nymserv', 'https://github.com/crooks/nymserv/commit/%ID', 'nymserv', 'stable' UNION"""
                #fde
                sql += """
                SELECT 1, 'http://encfs.googlecode.com/svn/trunk/', 'http://code.google.com/p/encfs/source/detail?r=%ID', 'encfs', 'stable' UNION
                SELECT 1, 'http://cryptsetup.googlecode.com/svn/trunk/', 'http://code.google.com/p/cryptsetup/source/detail?r=%ID', 'luks', 'pervasive' UNION"""
                #keyservers
                sql += """
                SELECT 6, 'http://www.earth.li/~noodles/bzr/onak/mainline', NULL, 'onak', 'development' UNION"""
                #otr
                sql += """
                SELECT 6, 'http://bazaar.launchpad.net/~afflux/python-otr/purepython', NULL, 'python-otr', 'beta' UNION"""
                #browser plugins
                sql += """
                SELECT 2, 'https://github.com/RC1140/cr-gpg.git', 'https://github.com/RC1140/cr-gpg/commit/%ID', 'cr-gpg', 'development' UNION"""
                #mailinglist
                sql += """
                SELECT 1, 'https://sels.svn.sourceforge.net/svnroot/sels', NULL, 'sels', 'development' UNION
                SELECT 8, 'http://non-gnu.uvt.nl/pub/mailman/', NULL, 'secure-list-server', 'development' UNION
                SELECT 2, 'git://git.immerda.ch/schleuder.git', NULL, 'schleuder', 'development' UNION
                SELECT 8, 'http://www.synacklabs.net/projects/crypt-ml/', NULL, 'crypt-ml', 'development' UNION
                SELECT 3, 'shibboleth.cvs.sourceforge.net', NULL, 'shibboleth', 'development' UNION
                SELECT 3, 'mmreencrypt.cvs.sourceforge.net', NULL, 'mmreencrypt', 'development'"""
                
                DB.execute(c, sql)

        #keyword._table + """ ---------------------------------------------
        if args.keywords:
            try:
                c.execute("DROP TABLE " + DB.keyword._table)        
            except:
                pass
        c.execute("SHOW TABLES LIKE '" + DB.keyword._table + "'")
        r = c.fetchone()
        if r:
            print "Keyword Table Exists"
        else:
            print "Creating Keyword Table..."
            sql = "CREATE TABLE " + DB.keyword._table + """
                    (
                    keyword varchar(50) NOT NULL,
                    parent varchar(50), 
                    type tinyint NOT NULL DEFAULT 1
                    ) ENGINE=innodb;
                    """
            c.execute(sql)
            
            if args.populate or args.keywords:
                print 'Populating Keywords...'

                h = open('tags.txt', 'r')
                sql = 'INSERT INTO ' + DB.keyword._table + "(keyword, parent, type)\n"
                components = []
                for l in h:
                    if not l.strip(): continue
                    parts = l.strip().split(':')
                    parts = [p.strip() for p in parts if p.strip()]
                    
                    if len(parts) > 1:
                        sql += "SELECT %s, %s, 1 UNION\n"
                        components.extend(parts)
                    else:
                        sql += "SELECT %s, NULL, 1 UNION\n"
                        components.append(parts[0])
                sql = sql[0:-6]
                DB.execute(c, sql, components)


                sql = "INSERT INTO " + DB.keyword._table + """(keyword, parent, type)
                SELECT 'openssl-library-bio', 'openssl-library', 3 UNION
                SELECT 'openssl-library-blowfish', 'openssl-library', 3 UNION
                SELECT 'openssl-library-bn', 'openssl-library', 3 UNION
                SELECT 'openssl-library-des', 'openssl-library', 3 UNION
                SELECT 'openssl-library-dh', 'openssl-library', 3 UNION
                SELECT 'openssl-library-dsa', 'openssl-library', 3 UNION
                SELECT 'openssl-library-err', 'openssl-library', 3 UNION
                SELECT 'openssl-library-evp', 'openssl-library', 3 UNION
                SELECT 'openssl-library-hmac', 'openssl-library', 3 UNION
                SELECT 'openssl-library-lhash', 'openssl-library', 3 UNION
                SELECT 'openssl-library-md5', 'openssl-library', 3 UNION
                SELECT 'openssl-library-mdc2', 'openssl-library', 3 UNION
                SELECT 'openssl-library-pem', 'openssl-library', 3 UNION
                SELECT 'openssl-library-rand', 'openssl-library', 3 UNION
                SELECT 'openssl-library-rc4', 'openssl-library', 3 UNION
                SELECT 'openssl-library-ripemd', 'openssl-library', 3 UNION
                SELECT 'openssl-library-rsa', 'openssl-library', 3 UNION
                SELECT 'openssl-library-sha', 'openssl-library', 3 UNION
                SELECT 'openssl-library-ssl', 'openssl-library', 3 UNION
                SELECT 'openssl-library-threads', 'openssl-library', 3 UNION
                SELECT 'openssl-library-x509', 'openssl-library', 3 UNION
                SELECT 'openssl-library', NULL, 3

                
                """
                c.execute(sql)
                
                #sql = "INSERT INTO " + DB.keyword._table + """(keyword, parent)
                #SELECT CONCAT('project-', r.tagname), NULL
                #FROM """ + DB.repo._table + " as r"
                #c.execute(sql)

                for f in os.listdir('keyword-setup'):
                    h = open('keyword-setup/' + f, 'r')
                    t = f.replace('.txt', '').replace("'", "") #rudimentary escaping here

                    sql = 'INSERT INTO ' + DB.keyword._table + "(keyword, parent, type)\n"
                    components = []
                    for l in h:
                        sql += "SELECT %s, '" + t + "', 2 UNION\n"
                        components.append(l.strip())
                    sql = sql[0:-6]
                    DB.execute(c, sql, components)


        #commit._table + """ ----------------------------------------
        c.execute("SHOW TABLES LIKE '" + DB.commit._table + "'")
        r = c.fetchone()
        if r:
            print "Commit Table Exists"
        else:
            print "Creating Commit Table..."
            sql = "CREATE TABLE " + DB.commit._table + """
                    (
                    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    repoid tinyint NOT NULL,
                    date int NOT NULL,
                    message text,
                    uniqueid varchar(64) NOT NULL,
                    UNIQUE (repoid, uniqueid)
                    ) ENGINE=innodb;
                    """
            c.execute(sql)
        #commitfile._table + """ ----------------------------------------
        c.execute("SHOW TABLES LIKE '" + DB.commitfile._table + "'")
        r = c.fetchone()
        if r:
            print "Commit File Table Exists"
        else:
            print "Creating Commit Table..."
            sql = "CREATE TABLE " + DB.commitfile._table + """
                    (
                    commitid int NOT NULL,
                    file varchar(512)
                    ) ENGINE=innodb;
                    """
            c.execute(sql)
        #commitkeyword._table + """ ----------------------------------------
        c.execute("SHOW TABLES LIKE '" + DB.commitkeyword._table + "'")
        r = c.fetchone()
        if r:
            print "Commit Keyword Table Exists"
        else:
            print "Creating Commit Keywords Table..."
            sql = "CREATE TABLE " + DB.commitkeyword._table + """
                    (
                    commitid int NOT NULL,
                    keyword varchar(50) NOT NULL,
                    PRIMARY KEY(commitid, keyword)
                    ) ENGINE=innodb;
                    """
            c.execute(sql)


    conn.commit()
