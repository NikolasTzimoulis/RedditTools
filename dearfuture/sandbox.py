#! python2
import googleCalendar
import datetime

googleCalendar.setCalendarID('o8oq4ir40k0j1g7umacsuhq8tk@group.calendar.google.com')
#googleCalendar.addEvent('sdas', datetime.datetime.utcnow(), description='lala', source='http://store.steampowered.com/')
events = googleCalendar.getEvents(datetime.datetime.utcnow(), datetime.datetime.utcnow()+datetime.timedelta(weeks=50))
for e in events:
    print e