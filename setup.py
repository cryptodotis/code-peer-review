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
				SELECT 2, 'https://github.com/cryptodotis/crypto.is-docs', 'crypto.is-docs', 'beta' UNION
				SELECT 2, 'https://github.com/moxie0/Convergence.git', 'convergence', 'beta' UNION
				SELECT 2, 'https://github.com/brl/obfuscated-openssh', 'obfuscated-openssh', 'stable' UNION
				SELECT 1, 'http://phantom.googlecode.com/svn/trunk/', 'phantom', 'development' UNION
				SELECT 8, 'http://www.agroman.net/corkscrew/', 'corkscrew', 'development' UNION
				SELECT 9, 'http://tahoe-lafs.org/source/tahoe-lafs/trunk/', 'tahoe-lafs', 'beta' UNION""" 
				#tor
				sql += """
				SELECT 2, 'https://gitweb.torproject.org/arm.git', 		'tor-arm', 		'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/bridgedb.git', 	'tor-bridgedb', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/debian/polipo.git', 	'tor-debian-polipo',	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/debian/tor.git', 	'tor-debian-tor', 	'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/flashproxy.git', 	'tor-flashproxy', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/gettor.git', 		'tor-gettor', 		'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/https-everywhere.git', 'https-everywhere', 	'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/jtorctl.git', 		'tor-jtorctl', 		'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/mat.git', 		'tor-mat', 		'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/metrics-db.git', 	'tor-metrics-db', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/metrics-tasks.git', 	'tor-metrics-tasks',	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/metrics-utils.git', 	'tor-metrics-utils, 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/metrics-web.git', 	'tor-metrics-web', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/obfsproxy.git', 	'tor-obfsproxy', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/orbot.git', 		'tor-orbot', 		'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/puppetor.git', 	'tor-puppetor', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/pytorctl.git', 	'tor-pytorctl', 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/thandy.git', 		'tor-thandy', 		'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/tor.git', 		'tor', 			'pervasive', UNION
				SELECT 2, 'https://gitweb.torproject.org/torbutton.git', 	'torbutton', 		'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/tordnsel.git', 	'tor-dnsel', 		'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/torsocks.git', 	'torsocks', 		'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/torspec.git', 		'torspec', 		'pervasive' UNION
				SELECT 2, 'https://gitweb.torproject.org/vidalia-plugins.git', 	'vidalia-plugins, 	'stable' UNION
				SELECT 2, 'https://gitweb.torproject.org/vidalia.git', 		'vidalia', 		'pervasive' UNION"""
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
				#browser plugins
				sql += """
				SELECT 2, 'https://github.com/RC1140/cr-gpg.git', 'cr-gpg', 'development' UNION"""
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
				
				SELECT 'project-cr-gpg', 'browser-plugin' UNION
				SELECT 'project-https-everywhere', 'browser-plugin' UNION
				
				SELECT 'project-enigmail', 'mailcient-plugin' UNION
				
				SELECT 'project-cr-gpg', 'email-crypto' UNION
				SELECT 'project-enigmail', 'email-crypto' UNION
				SELECT 'penango', 'email-crypto' UNION
				SELECT 'smime', 'email-crypto' UNION
				
				SELECT 'project-tor-debian-polipo', 'debian' UNION
				SELECT 'project-tor-debian-tor', 'debian' UNION
				SELECT 'debian', NULL UNION
				
				SELECT 'gentoo', NULL UNION
				SELECT 'ubuntu', NULL UNION
				
				SELECT 'oaep', 'crypto-padding' UNION
				SELECT 'oaep', 'asymmetric-crypto' UNION
				SELECT 'oaep', 'RSA' UNION
				
				SELECT 'dkim', NULL UNION

				SELECT 'vidalia', 'project-tor' UNION
				SELECT 'tor', 'project-tor' UNION
				
				SELECT 'project-tor-arm', 'project-tor' UNION
				SELECT 'project-tor-bridgedb', 'project-tor' UNION
				SELECT 'project-tor-debian-polipo', 'project-tor' UNION
				SELECT 'project-tor-debian-tor', 'project-tor' UNION
				SELECT 'project-tor-flashproxy', 'project-tor' UNION
				SELECT 'project-tor-gettor', 'project-tor' UNION
				SELECT 'project-tor-jtorctl', 'project-tor' UNION
				SELECT 'project-tor-mat', 'project-tor' UNION
				SELECT 'project-tor-metrics-db', 'project-tor' UNION
				SELECT 'project-tor-metrics-tasks', 'project-tor'UNION
				SELECT 'project-tor-metrics-utils, 'project-tor' UNION
				SELECT 'project-tor-metrics-web', 'project-tor' UNION
				SELECT 'project-tor-obfsproxy', 'project-tor' UNION
				SELECT 'project-tor-orbot', 'project-tor' UNION
				SELECT 'project-tor-puppetor', 'project-tor' UNION
				SELECT 'project-tor-pytorctl', 'project-tor' UNION
				SELECT 'project-tor-thandy', 'project-tor' UNION
				SELECT 'project-torbutton', 'project-tor' UNION
				SELECT 'project-tor-dnsel', 'project-tor' UNION
				SELECT 'project-torsocks', 'project-tor' UNION
				SELECT 'project-torspec', 'project-tor' UNION
				SELECT 'project-vidalia-plugins, 'project-vidalia' UNION
				SELECT 'project-vidalia', 'project-tor' UNION
				
				
				
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
