# -*- coding: utf-8 -*-
import praw
import datetime
import urllib

liverun = True

credFile = '../becareful.txt'
ourSub = 'Koina'
dateFormat = "%Y-%m-%dT%H:%M:%S.%f%z"
categories = {"invitemoderator": u"πρόσκληση νέου moderator",
              "uninvitemoderator": u"ανάκληση πρόσκλησης νέου moderator",              
              "addmoderator": u"προσθήκη νέου moderator",              
              "acceptmoderatorinvite": u"αποδοχή ως moderator",
              "removemoderator": u"διαγραφή από moderator",
              "addcontributor": u"προσθήκη ως approved submitter",
              "removecontributor": u"διαγραφή από approved submitter",              
              "banuser": u"αποβολή χρήστη",
              "unbanuser": u"ανάκληση αποβολής",              
              "approvecomment": u"έγκριση σχολίου",
              "distinguish": u"επισήμανση σχολίου",
              "showcomment": u"εμφάνιση σχολίου",                 
              "removecomment": u"αφαίρεση σχολίου",              
              "spamcomment": u"σπαμ σχόλιο",
              "sticky": u"καρφίτσωμα",              
              "unsticky": u"ξε-καρφίτσωμα",
              "approvelink": u"έγκριση ανάρτησης",
              "removelink": u"αφαίρεση ανάρτησης",
              "spamlink": u"αναφορά ανάρτησης ως σπαμ", 
              "unignorereports": u"μη-σίγαση reports",
              "ignorereports": u"σίγαση reports",
              "editflair": u"αλλαγή flair",              
              "setpermissions": u"αλλαγή εξουσιοδοτήσεων",
              "editsettings": u"αλλαγή ρυθμίσεων",              
              "wikirevise": u"επεξεργασία wiki",
              "add_community_topics": u"προσθήκη θεμάτων υπορέντιτ",
              "remove_community_topics": u"αφαίρεση θεμάτων υπορέντιτ",              
              "community_styling": u"επεξεργασία εμφάνισης", 
              "community_widgets": u"αλλαγή μπιχλιμπιδιών",  
              }
threadID = 'gzaml'

cred = list(map(lambda s: s.strip(), tuple(open(credFile, 'r'))))
r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])

thread = r.subreddit(ourSub).modmail(threadID)

lastTime = None
for msg in thread.messages:
    if msg.body_markdown.startswith("* "): lastTime = datetime.datetime.strptime(msg.date, dateFormat)

actions= []
for log in r.subreddit(ourSub).mod.log():
    date = datetime.datetime.fromtimestamp(log.created_utc, tz=datetime.timezone.utc)
    if date > lastTime and not log._mod == "AutoModerator":
        action = "* u/" + log._mod + ": " 
        subject = "Διαβούλευση για "
        message = "Διαφωνώ με την ατομική πρωτοβουλία "
        if log.action in categories:
            action += categories[log.action] + " "
            subject += categories[log.action] + " "
        else:
            action += log.action + " "
            subject += log.action + " "
        if log.description is not None:
            action += "(" + log.description + ") "
            subject += "(" + log.description + ") "
        if log.details is not None:
            action += "(" + log.details + ") " 
            subject += "(" + log.details + ") "
        if log.target_permalink is not None:
            linkshort = log.target_permalink.split('/')
            linkshort[5] = '-'
            linkshort = '/'.join(linkshort)
            actionshort = action[2:] + linkshort + " "
        else:
            actionshort = action[2:]
        if log.target_title is not None and log.target_permalink is not None: 
            action += "[" + log.target_title + "](" + linkshort + ") "
        elif log.target_permalink is not None and log.target_body is not None:
            action += "[" + log.target_body[:50].replace("\n", " ") + "](" + linkshort + ") "
        elif log.target_permalink is not None:
            action += linkshort + " "
        if len(log.target_author) >0 : 
            action += "(u/" + log.target_author + ") "
            actionshort += "(u/" + log.target_author + ") "
        message += actionshort + "άρα μπαίνει σε διαβούλευση και ψηφίζω κατά."
        link = "http://www.reddit.com/message/compose?"
        link += urllib.parse.urlencode({'to': "/r/"+ourSub, 'subject': subject, 'message': message}, safe='/') 
        print(action)
        action += "[❌](" + link + ")"
        actions.append(action)
       
actions.reverse()
while liverun and len(actions) > 0:
    alldone = False
    for i in range(len(actions)):
        output = "\n".join(actions[0:i])
        if len(output) > 10000:
            thread.reply("\n".join(actions[0:i-1]), internal=True)
            #print("\n".join(actions[0:i-1]))
            #print("-----")
            actions = actions[i-1:]
            break
        alldone = True
    if alldone:
        thread.reply("\n".join(actions), internal=True)
        #print("\n".join(actions))
        actions = []
thread.unread()
 