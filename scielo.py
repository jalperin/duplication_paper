import json
import urllib, urllib2

# install this from https://github.com/scieloorg/xylose
from xylose.scielodocument import Article

from ratelimited import RateLimited # to avoid hitting scielo too hard

from time import sleep, strftime, strptime
import datetime
import sys, os

import cPickle # for serializing and saving objects to disk
import shelve # for saving dictionaries to disk 

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('scielo.cnf')

import re, itertools, random  # some utils

ratelimited = RateLimited(15,1) # rate limit to 15 per second

def fetch_identifiers():
    '''
    This wil return the scielo identifiers
    either by querying them or by reading them from a file
    '''
    # do the fetch from API
    base_url = Config.get('api', 'base_url').strip('/')
    endpoint = Config.get('endpoints', 'identifiers')

    ## read in all the ISSNs from a file

    for issn in issns:
        data =  {'issn': issn}

        offset = 0
        while True:
            data['offset'] = offset
            url = base_url + endpoint + '?' + urllib.urlencode(data)
            content = json.load(ratelimited.urlopen(url))

            # do stuff here to work through the content


            offset = content['meta']['offset'] + len(content['objects'])

            # quit when we've reached the end
            if offset == content['meta']['total']:
                break



    # write ids to disk 
    return all_ids # this could be a set, or it could be a dict that maps issn->set of ids

def fetch_article(id, from_file = True):
    fname = Config.get('files', 'articlesfile')
    shelf = shelve.open(fname)

    if from_file and os.path.isfile(fname) and id in shelf:
        article = shelf[id]
        print 'from shelf'
    else:
        base_url = Config.get('articles', 'url').strip('/')
        endpoint = Config.get('endpoints', 'articles')
        data = {'code': id}
        url = base_url + endpoint + '?' + urllib.urlencode(data)
        content = json.load(ratelimited.urlopen(url))

        shelf[id] = content
        print "from API"
    shelf.close()

    return article