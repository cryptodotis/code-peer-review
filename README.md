#About

You're a developer. And you've spent the last 2 years working with Java sockets in an uninteresting trading app. But you also happen to support anonymity - but have no idea how to get involved. Or you're a security researcher who's spent the last two months understanding the padding oracle backwards and forwards. Wouldn't it be nice to see a personalized RSS feed of cryptography, anonymity, and privacy projects containing the keywords "java.net.Socket" or "CBC Mode"? Then you could skim commits, and if something interesting came up, you may be able to lend your expertise. That's exactly what the Code Peer Review is for.

# How You Can Help Test the Code Peer Review

From easiest to most time-intensive

## Help us add projects

 1. Without looking at [setup.py](https://github.com/cryptodotis/code-peer-review/blob/master/setup.py) think of all the crypto and privacy open source projects you can, and write them down.
 2. Check [setup.py](https://github.com/cryptodotis/code-peer-review/blob/master/setup.py) to see if you wrote down any we don't have yet
 3. Either fork and edit setup.py to include them, and submit a pull request, or just [create an issue](https://github.com/cryptodotis/code-peer-review/issues/new) and link to the project.
 
## Help us add tags

 1. Think of all the things you or someone else would be interested in code reviewing - crypto, threading, etc
 2. Check [tags.txt](https://github.com/cryptodotis/code-peer-review/blob/master/tags.txt) and see if they're there.
 3. Either fork and submit a pull request, or just [create an issue](https://github.com/cryptodotis/code-peer-review/issues/new) and tell us your tags
 
## Help us add library tags

 1. Find the API documentation for a crypto library - like OpenSSL
 2. Make textfiles that group the API function calls together (either into subgroups under the library or just all as the single library)
 3. Follow the format of [OpenSSL textfiles](https://github.com/cryptodotis/code-peer-review/tree/master/keyword-setup) 
 4. Fork and submit a pull request

## Run your own instance, and inspect the commits:

 1. Either set up your own instance of the Feed, or ask in #cryptodotis for the beta url 
 2. Put the raw RSS Feed in your favorite reader
 3. Review the commits to see if the code peer review missed a keyword, or see if you think of a new keyword should be added
 4. If you think of a UI feature that needs to be added, or something that's really missing, [create an issue](https://github.com/cryptodotis/code-peer-review/issues/new)
 
## Actively test the parser

 1. Set up your own instance of the Feed
 2. Change setup.py to contain your own test repositories
 3. ./setup.py --testpopulate
 4. Perform commits that should match tags, or perform commits on branches, or do strange commits (moves, renames, etc)
 5. ./cronjob -30 0  (for commits made 30 minutes ago)
 6. Make sure the Code Peer Review processes your test commits correctly.



# Requirements

 - Python
 - MySQL
 
 - pysvn
 - GitPython.  I'm using 0.3.2 RC1, I don't think 0.1 will work
  - [This patch applied](https://github.com/tomrittervg/GitPython/commit/0386f7ba2bedd8ae64040eb5f4d1246f0c4a2a1d) (Or figure out how to do diffing without it)
 - PLY (Python Lex-Yacc library), I'm using 3.4
 - PyRSS2Gen - I'm using 1.0.0
 - Jinja - I'm using 2.6
 - [Python-Graph](http://code.google.com/p/python-graph/) - I'm using 1.8.0 
 - google-diff-match-patch - I'm using 20111010
 - Tornado Webserver - I'm using 2.1.1

# Installation

 1. Move config.sample.py to config.py and fill in variables
 2. Run ./setup.py --populate or --testpopulate
 3. Set up a cronjob to run nightly with ./cronjob.py -86400 0
 4. python rss.py to run the rss feed/webserver temporarily, or use something similar to the included [gentoo-init-script](https://github.com/cryptodotis/code-peer-review/blob/master/gentoo-init-script) to run permanently
 5. Browse to localhost:8888/rss/ for the RSS Feed.
