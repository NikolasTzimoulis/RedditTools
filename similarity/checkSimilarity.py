#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
from collections import Counter
import math

reddit = "https://www.reddit.com/comments/"
delchars = " !\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
symbols = (u"άέήίόύώ", u"αεηιουω")
tr = dict( [ (ord(a), ord(b)) for (a, b) in zip(*symbols) ] )

user1 = "Anwnymia"
user2 = "Lafazanistan"
userProfiles = pickle.load(open("profiles.pickle", "rb"))

def prepare(profile):
    newProfile =[] 
    for comment in profile:
        newCommentData = set([])
        for word in comment[1]:
            newWord = word.strip(delchars)
            if len(newWord) >= 4:
                newWord = newWord.lower()
                newWord = newWord.translate(tr)
                newCommentData.add(newWord)
        newProfile.append((comment[0], newCommentData))
    return newProfile
        
def sim(comment1, comment2):
    i = len(comment1[1].intersection(comment2[1]))
    m = min(len(comment1[1]), len(comment2[1]))
    if m==0: return 0
    return 100*math.pow(i,2)/m
                
        

print "Preparing profiles...",
profile1 = prepare(userProfiles[user1])
profile2 = prepare(userProfiles[user2])
print "\t[DONE]"    

matrix = []
bestMatches = []
print "Calculating similarity matrix...",
for c1 in profile1:
    for c2 in profile2:
        s = sim(c1,c2)
        matrix.append(s)    
        if s>=300: bestMatches.append((len(c1[1].intersection(c2[1])), c1[0], c2[0], c1[1].intersection(c2[1])))        
print "\t[DONE]"

print Counter(matrix)
print min(matrix), max(matrix)
for match in bestMatches:
    print match[0]
    print reddit+match[1]
    print reddit+match[2]
    for w in match[3]: print w,
    print