import pickle

userProfiles = pickle.load(open("profiles.pickle", "rb"))

dictionary = {} 
for account in userProfiles:
    for comment in userProfiles[account]:
        for word in comment[1]:
            try:
                dictionary[word]+=1
            except:
                dictionary[word]=1
  
pickle.dump(dictionary, open("dict.pickle", "wb" ) )