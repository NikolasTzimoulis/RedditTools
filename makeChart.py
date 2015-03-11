import sqlite3
import matplotlib.pyplot
import os
import time

timePeriod = 24*60*60
allTogether = True

con = sqlite3.connect("karmaHistory.db")
with con:   
    cur = con.cursor()
    cur.execute("SELECT DISTINCT link FROM Comments")
    comments = [x[0] for x in cur.fetchall()]
    for c in comments:        
        cur.execute("SELECT time, score FROM Comments WHERE link = ?", [c])
        scores = cur.fetchall()
        if min([x[0] for x in scores]) >= time.time()-timePeriod:
            matplotlib.pyplot.plot([x[0] for x in scores], [y[1] for y in scores], 'ko:')
            if not allTogether:
                os.startfile(c)
                matplotlib.pyplot.show()
    matplotlib.pyplot.show()