import string
import datetime

dateFormats = ["%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y"]
falsePositiveAfterWordYear = ['ago', 'old', 'olds']
falsePositiveAfterNumberYear = ['x']

def getDates(words, now, strict=False):
    dates =[]
    for i in range(len(words)):
        strippedWord = words[i].strip(string.punctuation)
        for f in dateFormats:            
            try:
                d = datetime.datetime.strptime(strippedWord, f).date()
                if d > now.date():
                    dates.append((d, i))
                    break
            except:
                continue
        if strippedWord.isdigit() and len(words) > i+1 and words[i+1].startswith("year"):
            if not strict or len(words) <= i+2 or not words[i+2].strip(string.punctuation) in falsePositiveAfterWordYear: 
                dates.append((datetime.datetime(now.year+int(strippedWord), now.month, now.day),i+1))
        if strippedWord.isdigit() and int(strippedWord) > now.year and int(strippedWord) <= now.year+100:
            if not strict or len(words) <= i+1 or not words[i+1].strip(string.punctuation) in falsePositiveAfterNumberYear:
                dates.append((datetime.datetime(int(strippedWord), now.month, now.day),i+1))
    return dates