#! python2
import pickle
import datetime
import praw
import googleCalendar
import dateFunctions
import os

checkdateFileName = 'lastcheckdate.pkl'
credFile = '../secret.txt'
subredditName = 'DearFuture'
redditURL = 'http://www.reddit.com'
calendarID = 'o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com'
minScoreAllowed = 0
logFileName = 'sent.txt'
now = datetime.datetime.utcnow()

try:
    checkdateFile = open(checkdateFileName, 'rb')
    lastCheckDate = pickle.load(checkdateFile)
    checkdateFile.close()
except:
    lastId = None
    lastCheckDate = 0
    

cred = list(map(lambda s: s.strip(), tuple(open(credFile, 'r'))))

r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])    
submissions = r.subreddit(subredditName).new(limit=None)
googleCalendar.setCalendarID(calendarID)
updatedLastCheckDate = None
logFile = open(logFileName, 'w')

print("Collecting sent mail to the future...")

for s in submissions:
    if s.created_utc <= lastCheckDate: break
    if s.score < minScoreAllowed: continue
    if s.link_flair_text == u'inbox': continue
    words = s.title.split()
    dates = dateFunctions.getDates(words, now)
    for d in dates:
        toDate = d[0]
        fromDate = datetime.datetime.fromtimestamp(s.created_utc).date()
        if d[1] > 2:
            title = fromDate.strftime("FROM %Y/%m/%d: ") + ' '.join(words)
        else:
            title = fromDate.strftime("FROM %Y/%m/%d: ") + ' '.join(words[d[1]+1:])
        logFile.write(' '.join([str(s.score), s.title, s.permalink, '\n']).encode('utf-8'))
        googleCalendar.addEvent(title, toDate, description=s.permalink, source=s.url)
        s.flair.select(s.flair.choices()[1]['flair_template_id'])
    messageText = "I saw [your submission](" + s.permalink + ") on r/DearFuture "
    if dates:
        messageText += "and I will remind you about it on " + " and on ".join(map(lambda d:d[0].strftime("%Y/%m/%d"), dates)) + "."
    else:
        messageText += "but I didn't see any [future date](https://www.reddit.com/r/DearFuture/comments/3os3rc/) in the title."
    if not s.author.name == cred[4]: 
        s.author.message('/r/DearFuture Sent', messageText)
    if updatedLastCheckDate is None: updatedLastCheckDate = s.created_utc

for m in r.inbox.unread(limit=None):
    words = m.body.split()
    dates = dateFunctions.getDates(words, now)
    for d in dates:
        try:
            toDate = d[0]
            fromDate = datetime.datetime.fromtimestamp(m.created_utc).date()
            title = fromDate.strftime("FROM %Y/%m/%d: ") + m.submission.title
            if m.submission.comments[0].score < minScoreAllowed: continue
            logFile.write(' '.join([m.body, m.context, '\n']).encode('utf-8'))
            googleCalendar.addEvent(title, toDate, description=m.body, source=redditURL+m.context)
        except:
            continue
    m.mark_read()
    messageText = "I saw [your message](" + m.context + ") "  
    if dates:
        messageText += "and I will [remind you about it](/r/DearFuture) on " + " and on ".join(map(lambda d:d[0].strftime("%Y/%m/%d"), dates)) + "."
    else:
        messageText += "but I didn't see any [future date](https://www.reddit.com/r/DearFuture/comments/3os3rc/) included."
    m.author.message('/r/DearFuture Sent', messageText)
    
if updatedLastCheckDate is not None:  
    checkdateFile = open(checkdateFileName, 'wb')
    pickle.dump(updatedLastCheckDate, checkdateFile)
    checkdateFile.close()

logFile.close()
#os.startfile(logFileName)
