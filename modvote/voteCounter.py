# -*- coding: utf-8 -*-
import praw
import datetime
import math

liverun = True
specific = []

credFile = '../becareful.txt'
ourSub = 'Koina'
yper = [u"υπέρ", u"υπερ", u"yper", u"Υπέρ", u"Υπερ", u"Yper", u"ΥΠΕΡ", u"YPER"]
kata = [u"κατά", u"κατα", u"kata", u"Κατά", u"Κατα", u"Kata", u"ΚΑΤΑ", u"KATA"]
counter = [u"γύρο", u"μετράω", u"υπέρ", u"κατά", u"Άρα"]
oneWeek = datetime.timedelta(days=7)
dateFormat = "%Y-%m-%dT%H:%M:%S.%f%z"

cred = list(map(lambda s: s.strip(), tuple(open(credFile, 'r'))))
r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])

if len(specific) > 0:
    convList = map(lambda x:r.subreddit(ourSub).modmail(x), specific)
else:
    convList = r.subreddit(ourSub).modmail.conversations()

for conv in convList:
    output = ""
    votes = {}
    rounds = []
    prevCount = 0
    roundsCounted = 0
    needToPost = True
    messageList = conv.messages 
    messageList.append(praw.models.ModmailMessage(r, {"author":None, "body_markdown":"", "date":datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)}))
    for msg in messageList:
        user = msg.author
        theVote = None
        isCounter = False
        if user is None or user.is_subreddit_mod:
            yes = any(map(lambda x: x in msg.body_markdown, yper))
            no = any(map(lambda x: x in msg.body_markdown, kata))             
            if yes and not no:
                theVote = True
            elif no and not yes:
                theVote = False
            else:
                theVote = None
            if all(map(lambda x: x in msg.body_markdown, counter)):
                isCounter = True
                needToPost = False
                roundsCounted = len(rounds)
            msgDate = datetime.datetime.strptime(msg.date, dateFormat) if isinstance(msg.date, str) else msg.date 
            rYper = sum(v == True for v in votes.values())
            rKata = sum(v == False for v in votes.values())
            if len(rounds) > roundsCounted and rounds[-1] + oneWeek < msgDate and rYper+rKata >= 1.2 * prevCount:
                roundsCounted = len(rounds)
                if not isCounter: needToPost = True                     
                output += "Στον " + str(len(rounds))+ "ο γύρο μετράω " 
                output += str(rYper) + " υπέρ (" 
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
            if theVote is not None and (len(rounds) == 0 or rounds[-1] + oneWeek < msgDate and rYper+rKata >= 1.2 * prevCount):
                rounds.append(msgDate)
            if user is not None and (not user.name in votes or theVote is not None): 
                votes[user.name] = theVote
    if len(output) > 0:
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
            conv.highlight()
    else: print("\tOK")
