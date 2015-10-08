import pickle
import datetime
import praw
import googleCalendar

lastSubmitDateFileName = 'lastsubmitdate.pkl'
passwordFileName = 'password.pkl'
userName = 'futureMailBot'
subreddit = 'DearFuture'
calendarID = 'o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com'

print "Delivering to /r/DearFuture..."

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
for e in events:
    try:
        if e['description'].startswith('http'):
            link = e['description']
        else:
            link = e['source']['url']
        submission = r.submit(subreddit, e['summary'], url=link)
        r.set_flair(subreddit, submission, flair_text=u'inbox', flair_css_class=u'inbox')
        print e['summary']
    except:
        print "[FAILED] " + e['summary']

lastSubmitDateFile = open(lastSubmitDateFileName, 'wb')
pickle.dump(now, lastSubmitDateFile)
lastSubmitDateFile.close()