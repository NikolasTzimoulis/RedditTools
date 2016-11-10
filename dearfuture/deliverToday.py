import pickle
import datetime
import praw
import googleCalendar
import traceback
import os

lastSubmitDateFileName = 'lastsubmitdate.pkl'
passwordFileName = 'password.pkl'
logFileName = 'inbox.txt'
userName = 'futureMailBot'
subreddit = 'DearFuture'
calendarID = 'o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com'

print "Delivering to /r/DearFuture's inbox..."

try:
    lastSubmitDateFile = open(lastSubmitDateFileName, 'rb')
    lastSubmitDate = pickle.load(lastSubmitDateFile)
    lastSubmitDateFile.close()
except:
    lastSubmitDate = datetime.datetime(1, 1, 1)

try:
    passwordFile = open(passwordFileName, 'rb')
    passWord = pickle.load(passwordFile)
    passwordFile.close()
except:
    print "username: " + userName, "\npassword:",
    passWord = raw_input()
    passwordFile = open(passwordFileName, 'wb')
    pickle.dump(passWord, passwordFile)
    passwordFile.close()
    
r = praw.Reddit(user_agent=subreddit)
r.login(userName, passWord, disable_warning=True)
googleCalendar.setCalendarID(calendarID)
now = datetime.datetime.utcnow()
now = datetime.datetime(now.year, now.month, now.day) 
events = googleCalendar.getEvents(lastSubmitDate+datetime.timedelta(days=1), datetime.datetime(now.year, now.month, now.day, 23, 59))
logFile = open(logFileName, 'w')
for e in events:
    try:
        if e['description'].startswith('http'):
            link = e['description']
        else:
            link = e['source']['url']
        submission = r.submit(subreddit, e['summary'], url=link, resubmit=True)
        r.set_flair(subreddit, submission, flair_text=u'inbox', flair_css_class=u'inbox')
        print "[SUCCESS] ",
        logFile.write(e['summary'].encode('utf-8')+' ')
    except:
        print traceback.format_exc()
        print "[FAILED] ", 
        logFile.write("[FAILED] " + e['summary'].encode('utf-8'))
    try:
        original = r.get_submission(link)
        if original.permalink == link:
            r.send_message(original.author, '/r/DearFuture Inbox', '['+e['summary']+']('+submission.permalink+')')
        else:
            r.send_message(original.comments[0].author, '/r/DearFuture Inbox', '['+e['summary']+']('+submission.permalink+')')
        print " [PM SENT TO OP]"
        r.send_message("Naurgul", '/r/DearFuture Inbox', '['+e['summary']+']('+submission.permalink+')')
        logFile.write(" [PM SENT TO OP]\n")
    except:
        print " [FAILED TO PM OP]"
        logFile.write(" [FAILED TO PM OP]\n")

lastSubmitDateFile = open(lastSubmitDateFileName, 'wb')
pickle.dump(now, lastSubmitDateFile)
lastSubmitDateFile.close()
logFile.close()
#os.startfile(logFileName)