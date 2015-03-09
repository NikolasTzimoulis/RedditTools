import sqlite3
import matplotlib.pyplot
import os

firstComment = 0
lastComment = 10

con = sqlite3.connect("karmaHistory.db")
with con:   
    cur = con.cursor()
    cur.execute("SELECT DISTINcT link FROM Comments")
    comments = [x[0] for x in cur.fetchall()]
    for x in reversed(range(len(comments)-lastComment, len(comments)-firstComment)):
        os.startfile(comments[x])
        cur.execute("SELECT time, score FROM Comments WHERE link = ?", [comments[x]])
        scores = cur.fetchall()
        matplotlib.pyplot.plot([x[0] for x in scores], [y[1] for y in scores], 'ko:')
        matplotlib.pyplot.show()