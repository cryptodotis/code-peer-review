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
    def getChangedTextMetadata(self):
        return (self.uniqueid, self.repo)
    def getChangedTexts(self, metadata):
        if self.changedTexts != None:
            return self.changedTexts
        elif metadata == None:
            raise Exception("NULL passed to getChangedTexts when local changedTexts was not set")
            
        uniqueid, repo = metadata
        if int(uniqueid) == 1:
            diff = ''
        else:
            client = pysvn.Client()
            diff = client.diff(tmp_path='./', url_or_path=repo.url, 
                revision1=pysvn.Revision(pysvn.opt_revision_kind.number, int(uniqueid)-1), 
                revision2=pysvn.Revision(pysvn.opt_revision_kind.number, int(uniqueid)))
            diff = svn_diff_header.sub('', diff)
            diff = svn_diff_newline.sub('', diff)
            diff = svn_diff_property.sub('', diff)
            diff = svn_diff_deletions.sub('', diff)
            diff = diff.lower()
        self.changedTexts = [diff]
        return self.changedTexts