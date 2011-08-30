#!/usr/bin/python

import MySQLdb, argparse
from database import DB


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--wipe', dest='wipe', action='store_true', help='Instead of creating tables if they don\'t exist - empty the database.')
	parser.add_argument('--populate', dest='populate', action='store_true', help='If a reference data table is created, also populate it with some test data.  Mandatory refdata tables will be populated regardless.')
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
					tagname varchar(30) NOT NULL,
					maturity varchar(20) NOT NULL
					) ENGINE=innodb;
					"""
			c.execute(sql)
			
			if args.populate:
				print 'Populating Repos...'
				sql = "INSERT INTO " + DB.repo._table + """(repotypeid, url, tagname, maturity)
				SELECT 1, 'https://svn.torproject.org/svn/', 'tor', 'pervasive' UNION
				SELECT 2, 'https://github.com/cryptodotis/crypto.is-docs', 'crypto.is-docs', 'beta' UNION
				SELECT 2, 'https://github.com/moxie0/Convergence.git', 'convergence', 'beta' UNION
				SELECT 2, 'https://github.com/brl/obfuscated-openssh', 'obfuscated-openssh', 'stable' UNION
				SELECT 1, 'http://phantom.googlecode.com/svn/trunk/', 'phantom', 'development' UNION
				SELECT 8, 'http://www.agroman.net/corkscrew/', 'corkscrew', 'development' UNION
				SELECT 9, 'http://tahoe-lafs.org/source/tahoe-lafs/trunk/', 'tahoe-lafs', 'beta' UNION""" 
				#crypto libraries
				sql += """
				SELECT 2, 'git://git.gnupg.org/libgcrypt.git', 'libgcrypt', 'pervasive' UNION"""
				#file crypto
				sql += """
				SELECT 2, 'git://git.gnupg.org/gnupg.git', 'gnupg', 'pervasive' UNION"""
				#remailer
				sql += """
				SELECT 2, 'https://github.com/crooks/aam2mail.git', 'aam2mail', 'stable' UNION
				SELECT 2, 'https://github.com/crooks/nymserv', 'nymserv', 'stable' UNION"""
				#fde
				sql += """
				SELECT 1, 'http://encfs.googlecode.com/svn/trunk/', 'encfs', 'stable' UNION
				SELECT 1, 'http://cryptsetup.googlecode.com/svn/trunk/', 'luks', 'pervasive' UNION"""
				#keyservers
				sql += """
				SELECT 6, 'http://www.earth.li/~noodles/bzr/onak/mainline', 'onak', 'development' UNION"""
				#mailinglist
				sql += """
				SELECT 1, 'https://sels.svn.sourceforge.net/svnroot/sels', 'sels', 'development' UNION
				SELECT 8, 'http://non-gnu.uvt.nl/pub/mailman/', 'secure-list-server', 'development' UNION
				SELECT 2, 'git://git.immerda.ch/schleuder.git', 'schleuder', 'development' UNION
				SELECT 8, 'http://www.synacklabs.net/projects/crypt-ml/', 'crypt-ml', 'development' UNION
				SELECT 3, 'shibboleth.cvs.sourceforge.net', 'shibboleth', 'development' UNION
				SELECT 3, 'mmreencrypt.cvs.sourceforge.net', 'mmreencrypt', 'development'"""
				
				c.execute(sql)

		#keyword._table + """ ---------------------------------------------
		c.execute("SHOW TABLES LIKE '" + DB.keyword._table + "'")
		r = c.fetchone()
		if r:
			print "Keyword Table Exists"
		else:
			print "Creating Keyword Table..."
			sql = "CREATE TABLE " + DB.keyword._table + """
					(
					keyword varchar(50) NOT NULL,
					parent varchar(50) 
					) ENGINE=innodb;
					"""
			c.execute(sql)
			
			if args.populate:
				print 'Populating Keywords...'
				sql = "INSERT INTO " + DB.keyword._table + """(keyword, parent)
				
				SELECT 'project-schleuder', 'mailinglist' UNION
				SELECT 'project-sels', 'mailinglist' UNION
				SELECT 'project-secure-list-server', 'mailinglist' UNION
				SELECT 'project-mmreencrypt', 'mailinglist' UNION
				SELECT 'project-shibboleth', 'mailinglist' UNION
				SELECT 'project-crypt-ml', 'mailinglist' UNION
				
				SELECT 'project-onak', 'keyserver' UNION
				
				SELECT 'project-libgcrypt', 'library' UNION
				
				SELECT 'project-gnupg', 'filecrypto' UNION
				
				SELECT 'project-aam2mail', 'remailer' UNION
				SELECT 'project-nymserv', 'remailer' UNION
				SELECT 'pynchon', 'remailer' UNION
				SELECT 'underhill', 'remailer' UNION
				
				SELECT 'project-encfs', 'fde' UNION
				SELECT 'project-luks', 'fde' UNION
				
				
				SELECT 'debian', NULL UNION
				SELECT 'gentoo', NULL UNION
				SELECT 'ubuntu', NULL UNION
				
				SELECT 'oaep', 'crypto-padding' UNION
				SELECT 'oaep', 'asymmetric-crypto' UNION
				SELECT 'oaep', 'RSA' UNION
				
				SELECT 'dkim', NULL UNION

				SELECT 'vidalia', 'project-tor'
				
				
				
				"""
				c.execute(sql)
				
				sql = "INSERT INTO " + DB.keyword._table + """(keyword, parent)
				SELECT CONCAT('project-', r.tagname), NULL
				FROM """ + DB.repo._table + " as r"
				c.execute(sql)


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
