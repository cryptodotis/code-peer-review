#!/usr/bin/python

import git as pygit
import gdiff

from config import *
from commit import *

class GitCommit(Commit):
    def getDiffsArray(self):
        alldiffs = []
        differ = gdiff.diff_match_patch()
                
        commit = self.getChangedTextMetadata()
        for d in commit.diff(commit.__str__()+'^').iter_change_type('M'): #Changed
            left = d.a_blob.data_stream.read()
            right = d.b_blob.data_stream.read()
            alldiffs.append(differ.diff_main(left, right))

        for d in commit.diff(commit.__str__()+'^').iter_change_type('A'): #Added
            addition = d.b_blob.data_stream.read()
            alldiffs.append(differ.diff_main('', addition))

        return alldiffs
    def getChangedTextMetadata(self):
        localfolder = urlToFolder(self.repo.url)
        repoloc = Config.fsdir + 'git-repos/' + localfolder + '/'
        repo = pygit.Repo(repoloc)
                
        commit = repo.commit(self.uniqueid)
        return commit
    def getChangedTexts(self, commitobj):
        if self.changedTexts != None:
            return self.changedTexts
        elif commitobj == None:
            raise Exception("NULL passed to getChangedTexts when local changedTexts was not set")
            
        alldiffs = []
        differ = gdiff.diff_match_patch()
        
        for d in commitobj.diff(commitobj.__str__()+'^').iter_change_type('M'): #Changed
            left = d.a_blob.data_stream.read()
            right = d.b_blob.data_stream.read()
            diffs = differ.diff_main(left, right)
            if diffs: differ.diff_cleanupSemantic(diffs)

            for d in diffs:
                if d[0] != 0 and d[1].strip():
                    alldiffs.append(d[1].lower())

        for d in commitobj.diff(commitobj.__str__()+'^').iter_change_type('A'): #Added
            addition = d.b_blob.data_stream.read()
            alldiffs.append(addition.lower())
        #for d in commitobj.diff(commitobj.__str__()+'^').iter_change_type('D'): #Deleted
        #    pass
        #for d in commitobj.diff(commitobj.__str__()+'^').iter_change_type('R'): #Renamed
        #    pass
        self.changedTexts = alldiffs
        return self.changedTexts
