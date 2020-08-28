#! python2
import pickle
import datetime
import praw
import googleCalendar
import traceback
import os

lastSubmitDateFileName = 'lastsubmitdate.pkl'
passwordFileName = 'password.pkl'
logFileName = 'inbox.txt'
credFile = '../secret.txt'
subredditName = 'DearFuture'
calendarID = 'o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com'

print "Delivering to /r/DearFuture's inbox..."

try:
    lastSubmitDateFile = open(lastSubmitDateFileName, 'rb')
    lastSubmitDate = pickle.load(lastSubmitDateFile)
    lastSubmitDateFile.close()
except:
    lastSubmitDate = datetime.datetime(1, 1, 1)

   
cred = map(lambda s: s.strip(), tuple(open(credFile, 'r')))

r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])   
googleCalendar.setCalendarID(calendarID)
now = datetime.datetime.utcnow()
now = datetime.datetime(now.year, now.month, now.day) 
events = googleCalendar.getEvents(lastSubmitDate+datetime.timedelta(days=1), datetime.datetime(now.year, now.month, now.day, 23, 59))
sub = r.subreddit(subredditName)
logFile = open(logFileName, 'w')


for e in events:
    try:
        if 'description' in e and e['description'].startswith('http'):
            link = e['description']
        else:
            link = e['source']['url']
        submission = sub.submit(e['summary'], url=link, resubmit=True)
        submission.flair.select(submission.flair.choices()[0]['flair_template_id'])
        print "[SUCCESS] ",
        logFile.write(e['summary'].encode('utf-8')+' ')
    except:
        print traceback.format_exc()
        print "[FAILED] ", 
        logFile.write("[FAILED] " + e['summary'].encode('utf-8'))
    try:
        linkParts= link.split('/') 
        originalComment = r.comment(linkParts[-1] if linkParts[-1].isalnum() else linkParts[-2])
        originalSubmisson = r.submission(url=link) 
        try:
            originalComment.author.message('/r/DearFuture Inbox', '['+e['summary']+']('+submission.permalink+')')
        except:
            originalSubmisson.author.message('/r/DearFuture Inbox', '['+e['summary']+']('+submission.permalink+')')           
        print " [PM SENT TO OP]"
        logFile.write(" [PM SENT TO OP]\n")
    except:
        print " [FAILED TO PM OP]"
        logFile.write(" [FAILED TO PM OP]\n")

lastSubmitDateFile = open(lastSubmitDateFileName, 'wb')
pickle.dump(now, lastSubmitDateFile)
lastSubmitDateFile.close()
logFile.close()
#os.startfile(logFileName)