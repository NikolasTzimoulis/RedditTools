import pickle
import datetime
import praw
import googleCalendar
import dateFunctions
import os

checkdateFileName = 'lastcheckdate.pkl'
passwordFileName = 'password.pkl'
userName = 'futureMailBot'
subreddit = 'DearFuture'
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
submissions = r.get_subreddit(subreddit).get_new(limit=None)
googleCalendar.setCalendarID(calendarID)
updatedLastCheckDate = None
logFile = open(logFileName, 'w')

print "Collecting sent mail to the future..."

for s in submissions:
    if s.created_utc <= lastCheckDate: break
    if s.score < minScoreAllowed: continue
    words = s.title.split()
    dates = dateFunctions.getDates(words, now)
    for d in dates:
        toDate = d[0]
        fromDate = datetime.datetime.fromtimestamp(s.created_utc).date()
        title = fromDate.strftime("FROM %Y/%m/%d: ") + ' '.join(words[d[1]+1:])
        logFile.write(' '.join([str(s.score), s.title, s.permalink, '\n']).encode('utf-8'))
        googleCalendar.addEvent(title, toDate, description=s.permalink, source=s.url)
        r.set_flair(subreddit, s, flair_text=u'sent', flair_css_class=u'sent')
    messageText = "I saw [your submission](" + s.permalink + ") on r/DearFuture "
    if dates:
        messageText += "and I will remind you about it on " + " and on ".join(map(lambda d:d[0].strftime("%Y/%m/%d"), dates)) + "."
    else:
        messageText += "but I didn't see any [future date](https://www.reddit.com/r/DearFuture/comments/3os3rc/) in the title."
    if not s.author.name == userName: 
        r.send_message(s.author, '/r/DearFuture Sent', messageText)
        if not s.author.name == "Naurgul": r.send_message("Naurgul", '/r/DearFuture Sent', messageText) # for debugging
    if updatedLastCheckDate is None: updatedLastCheckDate = s.created_utc

for m in r.get_unread(limit=None):
    words = m.body.split()
    dates = dateFunctions.getDates(words, now)
    for d in dates:
        try:
            toDate = d[0]
            fromDate = datetime.datetime.fromtimestamp(m.created_utc).date()
            title = fromDate.strftime("FROM %Y/%m/%d: ") + m.submission.title
            if r.get_submission(m.permalink).comments[0].score < minScoreAllowed: continue
            logFile.write(' '.join([m.body, m.permalink, '\n']).encode('utf-8'))
            googleCalendar.addEvent(title, toDate, description=m.body, source=m.permalink)
        except:
            continue
    m.mark_as_read()
    messageText = "I saw [your message](" + m.permalink + ") "  
    if dates:
        messageText += "and I will [remind you about it](/r/DearFuture) on " + " and on ".join(map(lambda d:d[0].strftime("%Y/%m/%d"), dates)) + "."
    else:
        messageText += "but I didn't see any [future date](https://www.reddit.com/r/DearFuture/comments/3os3rc/) included."
    r.send_message(m.author, '/r/DearFuture Sent', messageText)
    if not m.author.name == "Naurgul": r.send_message("Naurgul", '/r/DearFuture Sent', messageText) # for debugging
    
if updatedLastCheckDate is not None:  
    checkdateFile = open(checkdateFileName, 'wb')
    pickle.dump(updatedLastCheckDate, checkdateFile)
    checkdateFile.close()

logFile.close()
#os.startfile(logFileName)
