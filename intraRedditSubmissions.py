import praw

subredditName = 'DepthHub'
credFile = 'secret.txt'

cred = map(lambda s: s.strip(), tuple(open(credFile, 'r')))
r = praw.Reddit(client_id=cred[0],
                     client_secret=cred[1],
                     password=cred[2],
                     user_agent=cred[3],
                     username=cred[4])   
freq = {}
for submission in  r.subreddit(subredditName).top('all', limit=1000):
    sub = submission.url
    sub = sub[sub.find('/r/')+3:]
    sub = sub[:sub.find('/')]
    if sub in freq:
        freq[sub] += 1
    else:
        freq[sub] = 1

for sub in sorted(freq.iterkeys(), key=lambda x:freq[x], reverse=True):
    print sub, freq[sub]