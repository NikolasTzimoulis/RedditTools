#! python2
import praw
import dateFunctions
import os
import datetime

ignoredSubsFile = 'ignoredsubs.txt'
logFileName = 'suggestions.txt'
logFile = open(logFileName, 'w')
subreddit = 'DearFuture'
now = datetime.datetime.utcnow()

print "Generating suggestions..."
r = praw.Reddit(user_agent=subreddit)
ignoredSubs = []
for line in open(ignoredSubsFile):
    ignoredSubs.append(line.strip()) 
for s in r.get_subreddit("all").get_top_from_day(limit=None):
    if s.score<200: break
    if s.subreddit.display_name not in ignoredSubs and (dateFunctions.getDates(s.title.split(), now, strict=True) or dateFunctions.getDates(s.selftext.split(), now, strict=True)): 
        logFile.write(' '.join([str(s.score), s.title, s.permalink, '\n']).encode('utf-8'))
logFile.close()
os.startfile(logFileName)
