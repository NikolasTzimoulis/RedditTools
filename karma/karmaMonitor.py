import praw
import sqlite3
import time

accountName = "naurgul"
sleepTime = 30*60
user_agent = ("Naurgul bot")
thing_limit = None
r = praw.Reddit(user_agent)

con = sqlite3.connect("karmaHistory.db")
with con:    
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE Posts(link TEXT, score INTEGER, time INTEGER);")
        cur.execute("CREATE TABLE Comments(link TEXT, score INTEGER, time INTEGER);")        
    except:
        pass

user = r.get_redditor(accountName)

while True:
    print "Downloading posts and comments...",
    posts = user.get_submitted(limit=thing_limit)
    comments = user.get_comments(limit=thing_limit)
    currentTime = time.time()
    with con:
        for thing in posts:
            cur.execute("INSERT INTO Posts VALUES(?, ?, ?)", [thing.short_link, thing.score, currentTime])
        for thing in comments:
            cur.execute("INSERT INTO Comments VALUES(?, ?, ?)", [thing._fast_permalink, thing.score, currentTime])
            
    print "\t [DONE]"
    print "Sleeping...",
    time.sleep(sleepTime)
    print "\t [DONE]"