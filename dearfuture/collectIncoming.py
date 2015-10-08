import pickle
import string
import datetime
import praw
import googleCalendar

checkdateFileName = 'lastcheckdate.pkl'
passwordFileName = 'password.pkl'
userName = 'futureMailBot'
subreddit = 'DearFuture'
calendarID = 'o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com'
minScoreAllowed = 1
delay = 2

print "Collecting future mail..."

try:
    checkdateFile = open(checkdateFileName, 'rb')
    lastCheckDate = pickle.load(checkdateFile)
    checkdateFile.close()
except:
    lastId = None
    
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
for s in submissions:
    if s.created_utc <= lastCheckDate: break
    if s.score < minScoreAllowed: continue
    titleWords = s.title.split()
    if titleWords[0].strip(string.punctuation).lower() != "to": continue
    try:
        toDate = datetime.datetime.strptime(titleWords[1].strip(string.punctuation), "%Y/%m/%d").date()
    except:
        continue
    fromDate = datetime.datetime.fromtimestamp(s.created_utc).date()
    title = fromDate.strftime("FROM %Y/%m/%d: ") + ' '.join(titleWords[2:])
    print s.title
    googleCalendar.addEvent(title, toDate, description=s.permalink, source=s.url)
    r.set_flair(subreddit, s, flair_text=u'sent', flair_css_class=u'sent')
    if updatedLastCheckDate is None: updatedLastCheckDate = s.created_utc


for m in r.get_unread(limit=None):
    words = m.body.split()
    for w in words:
        try:
            toDate = datetime.datetime.strptime(w.strip(string.punctuation), "%Y/%m/%d").date()
            fromDate = datetime.datetime.fromtimestamp(m.created_utc).date()
            title = fromDate.strftime("FROM %Y/%m/%d: ") + m.submission.title
            if r.get_submission(m.permalink).comments[0].score < minScoreAllowed: continue
            print m
            googleCalendar.addEvent(title, toDate, description=m.body, source=m.permalink)
        except:
            continue 
    m.mark_as_read()

if updatedLastCheckDate is not None:  
    checkdateFile = open(checkdateFileName, 'wb')
    pickle.dump(updatedLastCheckDate, checkdateFile)
    checkdateFile.close()
