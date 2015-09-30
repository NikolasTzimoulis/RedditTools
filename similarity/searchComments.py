#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
userName = 'kafros'
reddit = "https://www.reddit.com/comments/"
userProfiles = pickle.load(open("profiles.pickle", "rb"))
for c1 in userProfiles[userName]:
    if u'βγουμε' in c1[1]:
        print reddit+c1[0]