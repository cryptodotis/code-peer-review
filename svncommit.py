#!/usr/bin/python

import pysvn
import gdiff

from commit import *

class SVNCommit(Commit):
    def getDiffsArray(self):
        alldiffs = []
        differ = gdiff.diff_match_patch()
        client = pysvn.Client()
        
        for f in self.files:
            loc = self.repo.url + f
            loc = loc.replace("trunk//trunk", "trunk/")
            
            #Try/Catches are easier than seeing if the diff is an addition/deletion
            try:
                left = client.cat(url_or_path=loc, revision=pysvn.Revision(pysvn.opt_revision_kind.number, int(self.uniqueid)-1))
            except:
                left = ''
            try:
                right = client.cat(url_or_path=loc, revision=pysvn.Revision(pysvn.opt_revision_kind.number, int(self.uniqueid)))
            except:
                right = ''
                
            alldiffs.append(differ.diff_main(left, right))
        
        return alldiffs