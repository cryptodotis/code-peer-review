#!/usr/bin/python

import git as pygit
import gdiff

from config import *
from commit import *

class GitCommit(Commit):
    def getDiffsArray(self):
        alldiffs = []
        differ = gdiff.diff_match_patch()
        
        localfolder = urlToFolder(self.repo.url)
        repoloc = Config.fsdir + 'git-repos/' + localfolder + '/'
        repo = pygit.Repo(repoloc)
                
        commit = repo.commit(self.uniqueid)
        for d in commit.diff(commit.__str__()+'^').iter_change_type('M'): #Changed
            left = d.a_blob.data_stream.read()
            right = d.b_blob.data_stream.read()
            alldiffs.append(differ.diff_main(left, right))

        for d in commit.diff(commit.__str__()+'^').iter_change_type('A'): #Added
            addition = d.b_blob.data_stream.read()
            alldiffs.append(differ.diff_main('', addition))

        return alldiffs
