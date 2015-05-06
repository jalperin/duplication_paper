import re
from collections import defaultdict
from collections import Counter

import simplejson as json

from datetime import datetime

# Create a dict keyed on metric type
posts = defaultdict(list)
with open('data/altmetric_com.txt', 'r') as content_file:
    i = 0
    for p in content_file:
        line = p.split()
        metric = line[1]
        post = json.loads(' '.join(line[2:]))
        posts[metric].append(post)
        i+=1
        
print [(x, len(y)) for x,y in posts.iteritems()]


scielo_domain_regex = re.compile(r'https?:\/\/(?:www\.)?(scielo[a-z\.]+[a-z])', re.IGNORECASE)
redalyc_domain_regex = re.compile(r'https?:\/\/(?:www\.)?(redalyc\.org)', re.IGNORECASE)

scielo_article_regex = re.compile(r'[\&\?]pid=([Ss\d\-]+)', )
redalyc_article_regex = re.compile(r'articulo.oa?\?id=(\d\d\d\d\d+)')

# tweets = filter(lambda t: len(filter(lambda l: domain_regex.search(l), t['links'])) > 0, )
# print len(tweets)

articles = defaultdict(lambda: defaultdict(int))
domains = defaultdict(list)
tweeters = set()

def count_metrics(metric, links):
    global articles
    
    for l in links:
        scielo_match = scielo_domain_regex.search(l)
        redalyc_match = redalyc_domain_regex.search(l)
        if scielo_match:
            matches = scielo_article_regex.search(l)
            if matches:
                articles[matches.group(1).upper()][metric] += 1
                return scielo_match
            
        elif redalyc_match:
            matches = redalyc_article_regex.search(l)
            if matches:
                articles[matches.group(1)][metric] += 1
            return redalyc_match

# i = 0
for m, p in posts.iteritems():
    for post in p: 
        if post['posted_on'] >= int(datetime(2013,1,1).strftime("%s")):
            matches = count_metrics(m, post['links'])
            if matches:
                domains[matches.group(1).lower()].append(post['posted_on'])
                try:
                    if post['tweeter_id'] == '148474702':
                        print post
                        
                    tweeters.add(post['tweeter_id'])
                except KeyError:
                    pass   # this is just that the metric was probably not Twitter, so no tweeter_id
                

print "Found %s articles with a total of %s metrics" % (len(articles), sum([articles[a][m] for a in articles for m in articles[a]]))
print "Found %s tweeters" % (len(tweeters))