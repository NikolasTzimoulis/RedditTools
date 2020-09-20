import praw
import webbrowser

sponsored = ["TurbulentSoftBurger"]

credFile = '../becareful.txt'
ourSub = 'Koina'
threadLink = 'https://mod.reddit.com/mail/mod/bplm5'

cred = list(map(lambda s: s.strip(), tuple(open(credFile, 'r'))))
r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])

found = False
for item in r.subreddit(ourSub).mod.spam(limit=None):
    if item.author is not None and item.author.name in sponsored:
        found = True
        webbrowser.open("https://www.reddit.com" + item.permalink, new=2)
if found:
    webbrowser.open(threadLink, new=2)