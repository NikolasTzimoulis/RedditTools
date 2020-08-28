#!/usr/bin/env python
# -*- coding: utf-8 -*-
import praw
import pickle
import re

delchars = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
symbols = (u"άέήίόύώ", u"αεηιουω")
tr = dict( [ (ord(a), ord(b)) for (a, b) in zip(*symbols) ] )

def extract(comment):
    e = set([])
    for word in re.split("["+delchars+"]", comment.body): 
        if len(word)==0: continue 
        newWord = word.lower()
        newWord = newWord.translate(tr)
        e.add(newWord)
    return (comment._fast_permalink[32:], e)

accountNames = ["USERNAME1", "USERNAME2"]

user_agent = ("Naurgul bot")
thing_limit = None

r = praw.Reddit(user_agent)

userProfiles = {}
for acc in accountNames:
    user = r.get_redditor(acc)
    print "Downloading /u/"+acc+"'s comments...",
    comments = user.get_comments(limit=thing_limit)
    userProfiles[acc] = map(extract, comments)
    print "\t[DONE]"     
    
pickle.dump(userProfiles, open( "profiles.pickle", "wb" ) )
        
