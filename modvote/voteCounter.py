# -*- coding: utf-8 -*-
import praw
import datetime
import math
import string
import itertools

liverun = True
specific = []
convLimit = 100

credFile = '../becareful.txt'
ourSub = 'Koina'
yper = [u"υπέρ", u"υπερ", u"yper", u"Υπέρ", u"Υπερ", u"Yper", u"ΥΠΕΡ", u"YPER"]
kata = [u"κατά", u"κατα", u"kata", u"Κατά", u"Κατα", u"Kata", u"ΚΑΤΑ", u"KATA"]
counter = [u"γύρος", u"Μετράω", u"υπέρ", u"κατά", u"Άρα"]
close = [u"κλείσει", u"οριστικά", u"40", u"λήξη", u"τελευταίου", u"μέλλον", u"μεταβάλλει"]
oneWeek = datetime.timedelta(days=7)
fortyDays = datetime.timedelta(days=40)
dateFormat = "%Y-%m-%dT%H:%M:%S.%f%z"
rightNow = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

cred = list(map(lambda s: s.strip(), tuple(open(credFile, 'r'))))
r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])

convWithVotes = {}

if len(specific) > 0:
    convList = map(lambda x:r.subreddit(ourSub).modmail(x), specific)
else:
    convList = itertools.chain(r.subreddit(ourSub).modmail.conversations(limit=convLimit), r.subreddit(ourSub).modmail.conversations(state="mod", limit=convLimit))


for conv in convList:
    output = ""
    votes = {}
    rounds = []
    prevCount = 0
    roundsCounted = 0
    needToPost = True
    isClosed = False
    messageList = r.subreddit(ourSub).modmail(conv.id).messages
    messageList.append(praw.models.ModmailMessage(r, {"id":None, "author":None, "body_markdown":"", "date":rightNow}))
    for msg in messageList:
        user = msg.author
        theVote = None
        isCounter = False
        if user is None or user.is_subreddit_mod:
            msgWords = [x.strip(string.punctuation) for x in msg.body_markdown.split()]
            yes = any(map(lambda x: x in msgWords, yper))
            no = any(map(lambda x: x in msgWords, kata))             
            if yes and not no:
                theVote = True
            elif no and not yes:
                theVote = False
            else:
                theVote = None
            if all(map(lambda x: x in msg.body_markdown, counter)):
                isCounter = True
                needToPost = False
            if all(map(lambda x: x in msg.body_markdown, close)):
                isClosed = True  
                output = ""
            msgDate = datetime.datetime.strptime(msg.date, dateFormat) if isinstance(msg.date, str) else msg.date 
            rYper = sum(v == True for v in votes.values())
            rKata = sum(v == False for v in votes.values())
            if len(rounds) > roundsCounted and rounds[-1] + oneWeek < msgDate and rYper+rKata >= 1.2 * prevCount:
                roundsCounted += 1
                if not isCounter: needToPost = True                     
                output += "Ο " + str(len(rounds))+ "ος γύρος έληξε στις "                
                output +=  (rounds[-1] + oneWeek).strftime("%d/%m, %H:%M. ")
                output += "Μετράω " + str(rYper) + " υπέρ (" 
                output += ", ".join(filter(lambda u: votes[u] == True, votes.keys())) + ") και "
                output +=  str(rKata) + " κατά ("
                output += ", ".join(filter(lambda u: votes[u] == False, votes.keys())) + "). "
                if float(rYper) / (rYper + rKata) >= 0.6:
                    output += "Άρα εγκρίθηκε με " + str(round(100.0 * rYper / (rYper + rKata))) + "% πλειοψηφία"
                    if rYper + rKata < 6:
                        output += ", εκτός αν πρόκειται για ένταξη ή αποβολή μέλους"
                    elif rYper + rKata < 10:
                        output += ", εκτός αν πρόκειται για αποβολή μέλους"
                    output += ".\n\n"
                else:
                    output += "Άρα απορρίφθηκε καθώς " + str(round(100.0 * rYper / (rYper + rKata))) + "% < 60%.\n\n"
                prevCount = rYper + rKata
            if not isClosed and len(rounds) > 0 and rounds[-1] + oneWeek + fortyDays < msgDate:
                needToPost = True
                output = "Η διαβούλευση έχει κλείσει οριστικά καθώς πέρασαν 40 μέρες από τη λήξη του τελευταίου γύρου.\n\n"
                output += "Αν στο μέλλον υπάρξει διαβούλευση που μεταβάλλει το πιο πάνω αποτέλεσμα, απαιτείται να έχει τουλάχιστο " + str(math.ceil(prevCount*0.4)) + " ψήφους."
                isClosed = True  
            if theVote is not None and (len(rounds) == 0 or rounds[-1] + oneWeek < msgDate and rYper+rKata+1 >= 1.2 * prevCount and not isClosed):
                rounds.append(msgDate)
            if user is not None and (not user.name in votes or theVote is not None): 
                votes[user.name] = theVote
                if theVote is not None and msgDate + oneWeek > rightNow: 
                    convWithVotes[conv.id] = (msgDate, conv.subject, conv.user.name if hasattr(conv, 'user') else "", sum(v == True or v == False for v in votes.values()))              
    if len(output) > 0 and not isClosed:
        output += "Η τρέχουσα διαβούλευση είναι άκυρη αν μεταβάλλει παλιότερη απόφαση που πάρθηκε με περισσότερες από " + str(math.floor(prevCount/0.4)) + " ψήφους.\n\n"
        output += "Απαιτούνται " + str(math.ceil(prevCount*0.2)) + " νέες ψήφοι για έναρξη επόμενου γύρου.\n\n"
        observers = list(filter(lambda u: votes[u] == None, votes.keys()))
        if len(observers) > 0:
            output += "ΥΓ: Συμμετείχαν στη συζήτηση χωρίς να ψηφίσουν οι " + ", ".join(observers) + ".\n\n"
    print(conv.subject, "https://mod.reddit.com/mail/all/"+conv.id, end='')
    if len(output) > 0 and needToPost:
        print()
        print(output)      
        if liverun: 
            conv.reply(output, internal=True)
            conv.unread()
            if not isClosed: 
                conv.highlight()
    else: print("\tOK")

if rightNow.weekday() == 6 and len(convWithVotes) > 0 and len(specific) == 0:
    weeklySummary = "Ορίστε οι διαβουλεύσεις που έχουν λάβει ψήφους την τελευταία εβδομάδα:\n\n"
    for conv in sorted(list(convWithVotes.keys()), key=(lambda x: convWithVotes[x][0])):
        weeklySummary += "* [" + convWithVotes[conv][1] + "](https://mod.reddit.com/mail/all/" + conv + ") " 
        weeklySummary += "(u/" +  convWithVotes[conv][2] + ") " if not convWithVotes[conv][2] == ""  else "" 
        weeklySummary += "(" + str(convWithVotes[conv][3]) + " ψήφοι)\n" 
    weeklySummary += "\n\nΠάρθηκε απόφαση που δε σου άρεσε αλλά δεν τη βρίσκεις παραπάνω επειδή έγινε με ατομική πρωτοβουλία; [Πήγαινε στο Ιστορικό](https://mod.reddit.com/mail/mod/gzaml) κι από εκεί μπορείς να την βάλεις σε διαβούλευση πατώντας το ❌."
    weeklySummary += "\n\nΔε σε αφήνει ούτε καν να μπεις στις διαβουλεύσεις; Αυτό σημαίνει ότι δεν είσαι ακόμα μέλος του r/koina. [Στείλε ένα modmail](https://www.reddit.com/message/compose?to=%2Fr%2FKoina&subject=Πρόσκληση) για να γίνεις."
    print(weeklySummary)
    if liverun:
        submission = r.subreddit(ourSub).submit(title="Πρόσφατες διαβουλεύσεις", selftext=weeklySummary)
        submission.flair.select(submission.flair.choices()[0]['flair_template_id'], text="META")