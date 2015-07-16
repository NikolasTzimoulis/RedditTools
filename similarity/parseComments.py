import praw
import pickle

def extract(comment):
    e = set([])
    for word in comment.body.split():
        e.add(word)
    return (comment._fast_permalink[32:], e)

accountNames = ["fateswarm", "AThinker", "PrincessDanna", "Anwnymia", "Lafazanistan", "Samaristan"]

user_agent = ("Naurgul bot")
thing_limit = None

r = praw.Reddit(user_agent)

userProfiles = {}
for acc in accountNames:
    user = r.get_redditor(acc)
    print "Downloading /u/"+acc+"'s comments...",
    comments = user.get_comments(limit=thing_limit)
    userProfiles[acc] = map(extract, comments) 
    print "\t[DONE]"
     
    
pickle.dump(userProfiles, open( "profiles.pickle", "wb" ) )
        
