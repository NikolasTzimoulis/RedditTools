import pickle
from collections import Counter
import math

reddit = "https://www.reddit.com/comments/"

user1 = "AThinker"
user2 = "PrincessDanna"
similarityThreshold = 30

userProfiles = pickle.load(open("profiles.pickle", "rb"))
dictionary = pickle.load(open("dict.pickle", "rb"))
        
def sim(comment1, comment2):
    freqList = map(lambda x: 1.0/math.pow(dictionary[x],2), comment1[1].intersection(comment2[1]))
    return int(100*sum(freqList))

matrix = []
bestMatches = []
print "Calculating similarity matrix...",
for c1 in userProfiles[user1]:
    for c2 in userProfiles[user2]:
        s = sim(c1,c2)
        matrix.append(s)    
        if s>=similarityThreshold: bestMatches.append((sim(c1,c2), c1[0], c2[0], sorted( c1[1].intersection(c2[1]), key=lambda x:dictionary[x]) ))        
print "\t[DONE]"

print Counter(matrix)
print min(matrix), max(matrix)
for match in sorted(bestMatches, key=lambda x:x[0], reverse=True):
    print match[0]
    print reddit+match[1]
    print reddit+match[2]
    for w in match[3]: print w,
    print