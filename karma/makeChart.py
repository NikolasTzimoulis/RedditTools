import sqlite3
import matplotlib.pyplot
import os
import time

timePeriod = 1*24*60*60 # in seconds
allTogether = True # if true print one chart, if false print one chart per post/comment
posts = False # if true we chart submissions, if false we chart comments
link = 'http://www.reddit.com/comments/37yqgi/_/crr96oa' #None

now = time.time()
con = sqlite3.connect("karmaHistory.db")
with con:   
    cur = con.cursor()
    if link is None:
        if posts:
            cur.execute("SELECT DISTINCT link FROM Posts")
        else:
            cur.execute("SELECT DISTINCT link FROM Comments")
        things = [x[0] for x in cur.fetchall()]
    else:
        things = [link]
    for t in things:   
        if posts:
            cur.execute("SELECT time, score FROM Posts WHERE link = ?", [t])
        else:
            cur.execute("SELECT time, score FROM Comments WHERE link = ?", [t])
        scores = cur.fetchall()
        if link is not None or min([x[0] for x in scores]) >= time.time()-timePeriod:
            matplotlib.pyplot.plot([(x[0]-now)/60/60 for x in scores], [y[1] for y in scores], 'ko:')
            if not allTogether:
                os.startfile(t)
                matplotlib.pyplot.show()
    matplotlib.pyplot.show()