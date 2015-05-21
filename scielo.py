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
 
def fetch_identifiers(from_file=True):
    '''
    Returns the scielo identifiers
    either by querying them or by reading them from a file
    '''
    
    issnDict = dict() #map ISSN to set of identifiers
    fname = Config.get('issns', 'issnsfile')
    shelf = shelve.open(fname)
    
    empty = open('empty-issns.txt', 'r+b') #List of ISSNs that have no identifiers
    empty.truncate()
    
    f = open('issns.txt', 'rb')
    
    #Go through txt file line by line 
    for line in f: 
        issn = line.rstrip('\n')
        articleSet = set()
         
       
        if from_file and os.path.isfile(fname) and issn in shelf:
            #Read from shelf
            articleSet = shelf[issn]
            issnDict[issn] = articleSet
            print 'from shelf'
        else:    
            # do the fetch from API
            print 'from API'
            base_url = Config.get('api', 'base_url').strip('/')
            endpoint = Config.get('endpoints', 'identifiers')
            data =  {'issn': issn}
     
            offset = 0
            while True:
                data['offset'] = offset         
                url = base_url + endpoint + '?' + urllib.urlencode(data)
                content = json.load(ratelimited.urlopen(url))
                
                for article in content['objects']:
                    articleSet.add(article['code'].encode('utf-8'))
                
                offset = content['meta']['offset'] + len(content['objects'])
               
                # quit when we've reached the end
                if offset == content['meta']['total']:
                    if articleSet: 
                        # write ids to disk
                        shelf[issn] = articleSet
                        issnDict[issn] = articleSet
                    else:
                        #Make a note that the ISSN was empty
                        empty.write(issn + '\n')
                        
                    
                    break
    shelf.close()
    empty.close()
    f.close()
    
#    return all_ids as a dict that maps issn->set of ids
    print issnDict        
    return issnDict
    
 
def fetch_article(id, from_file = True):
    article = ''
    
    
    fname = Config.get('files', 'articlesfile')
    shelf = shelve.open(fname)
    
 
    if from_file and os.path.isfile(fname) and id in shelf:
        #Read from shelf
        article = shelf[id]
        print 'from shelf'
    else:
        #Fetch from API
        base_url = Config.get('api', 'base_url').strip('/')
        endpoint = Config.get('endpoints', 'articles')
        data = {'code': id}
        url = base_url + endpoint + '?' + urllib.urlencode(data)
        article = json.load(ratelimited.urlopen(url))
        shelf[id] = article
        print "from API"
    
    shelf.close()
    return article


#Test
ids = fetch_identifiers()

for value in ids.itervalues():
    for identifier in value: 
        fetch_article(identifier)
