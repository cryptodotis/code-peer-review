#!/usr/bin/python

class Config:
    username=""
    password=""
    host="localhost"
    database=""

    tornadoport=8888# port you want Tornado to listen on
    rooturl="http://example.com" #no trailing slash
    fsdir="/var/www/htdocs/containingDirOfPyFiles/" #trailing slash
    logfile="/var/log/tornado/tornado_log"
