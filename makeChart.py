import sqlite3
import matplotlib.pyplot
import os

firstComment = 0
lastComment = 5
allTogether = True

con = sqlite3.connect("karmaHistory.db")
with con:   
    cur = con.cursor()
    cur.execute("SELECT DISTINcT link FROM Comments")
    comments = [x[0] for x in cur.fetchall()]
    for c in reversed(range(len(comments)-lastComment, len(comments)-firstComment)):        
        cur.execute("SELECT time, score FROM Comments WHERE link = ?", [comments[c]])
        scores = cur.fetchall()
        matplotlib.pyplot.plot([x[0] for x in scores], [y[1] for y in scores], 'ko:')
        if not allTogether:
            os.startfile(comments[c])
            matplotlib.pyplot.show()
    matplotlib.pyplot.show()