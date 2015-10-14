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
dateFormats = ["%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y"]
now = datetime.datetime.utcnow()

print "Collecting future mail..."

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
    
def getDates(words):
    dates =[]
    for i in range(len(words)):
        for f in dateFormats:            
            try:
                d = datetime.datetime.strptime(words[i].strip(string.punctuation), f).date()
                dates.append((d, i))
                break
            except:
                continue
        if words[i].strip(string.punctuation).isdigit() and len(words) > i+1 and words[i+1].startswith("year"):
            dates.append((datetime.datetime(now.year+int(words[i]), now.month, now.day),i+1))
    return dates

r = praw.Reddit(user_agent=subreddit)
r.login(userName, passWord, disable_warning=True)
submissions = r.get_subreddit(subreddit).get_new(limit=None)
googleCalendar.setCalendarID(calendarID)
updatedLastCheckDate = None
for s in submissions:
    if s.created_utc <= lastCheckDate: break
    if s.score < minScoreAllowed: continue
    words = s.title.split()
    dates = getDates(words)
    for d in dates:
        toDate = d[0]
        fromDate = datetime.datetime.fromtimestamp(s.created_utc).date()
        title = fromDate.strftime("FROM %Y/%m/%d: ") + ' '.join(words[d[1]+1:])
        if toDate > now.date():
            print s.title
            googleCalendar.addEvent(title, toDate, description=s.permalink, source=s.url)
            r.set_flair(subreddit, s, flair_text=u'sent', flair_css_class=u'sent')
            if updatedLastCheckDate is None: updatedLastCheckDate = s.created_utc


for m in r.get_unread(limit=None):
    words = m.body.split()
    dates = getDates(words)
    for d in dates:
        toDate = d[0]
        fromDate = datetime.datetime.fromtimestamp(m.created_utc).date()
        title = fromDate.strftime("FROM %Y/%m/%d: ") + m.submission.title
        if r.get_submission(m.permalink).comments[0].score < minScoreAllowed: continue
        print m
        googleCalendar.addEvent(title, toDate, description=m.body, source=m.permalink)
    m.mark_as_read()

if updatedLastCheckDate is not None:  
    checkdateFile = open(checkdateFileName, 'wb')
    pickle.dump(updatedLastCheckDate, checkdateFile)
    checkdateFile.close()
