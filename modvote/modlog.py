# -*- coding: utf-8 -*-
import praw
import datetime

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
              "distinguish ": u"επισήμανση σχολίου",
              "showcomment ": u"εμφάνιση σχολίου",                 
              "removecomment ": u"αφαίρεση σχολίου",              
              "spamcomment": u"σπαμ σχόλιο",
              "sticky ": u"καρφίτσωμα ανάρτησης",              
              "unsticky ": u"ξε-καρφίτσωμα ανάρτησης",
              "approvelink ": u"έγκριση ανάρτησης",
              "removelink": u"αφαίρεση ανάρτησης",
              "spamlink": u"σπαμ ανάρτηση", 
              "unignorereports": u"μη-σίγαση reports",
              "ignorereports": u"σίγαση reports",
              "editflair": u"αλλαγή flair",              
              "setpermissions": u"αλλαγή εξουσιοδοτήσεων",
              "editsettings": u"αλλαγή ρυθμίσεων",              
              "wikirevise": u"επεξεργασία [wiki](/r/Koina/wiki/revisions/index)",
              "add_community_topics": u"προσθήκη θεμάτων υπορέντιτ",
              "remove_community_topics": u"αφαίρεση θεμάτων υπορέντιτ",              
              "community_styling": u"επεξεργασία εμφάνισης",                            
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

output = ""
for log in r.subreddit(ourSub).mod.log():
    date = datetime.datetime.fromtimestamp(log.created_utc, tz=datetime.timezone.utc)
    if date > lastTime and not log._mod == "AutoModerator":
        output += "* u/" + log._mod + ": " 
        if log.action in categories:
            output += categories[log.action] + " "
        else:
            output += log.action + " "
        if log.description is not None:
            output += "(" + log.description + ") "
        if log.details is not None:
            output += "(" + log.details + ") " 
        if log.target_title is not None and log.target_permalink is not None: 
            output += "[" + log.target_title + "](" + log.target_permalink + ") "
        elif log.target_permalink is not None and log.target_body is not None:
            output += "[" + log.target_body[:50] + "](" + log.target_permalink + ") "
        elif log.target_permalink is not None:
            output += log.target_permalink + " "
        if len(log.target_author) >0 : 
            output += "(u/" + log.target_author + ")"
        output += "\n"
        
print(output)
if liverun and len(output) > 0:
    thread.reply(output, internal=True)
 