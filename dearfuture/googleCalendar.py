import datetime
import httplib2
import os
import urllib2
from BeautifulSoup import BeautifulSoup

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools



try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
    
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar Python Easy Library'
CALENDAR_ID = None
service = None


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

def setCalendarID(calendarID):
    global CALENDAR_ID, service
    CALENDAR_ID = calendarID
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

def createEvent(title, startTime, endTime, description, source):
    return {
  'summary': title,
  'location': '',
  'description': description,
  'start': {
    'dateTime': startTime,
    'timeZone': '',
  },
  'end': {
    'dateTime': endTime,
    'timeZone': '',
  },
  'recurrence': [],
  'attendees': [],
  'reminders': {
    'useDefault': True,
    'overrides': [],
  },
  "source": {
    "url": source,
    "title": BeautifulSoup(urllib2.urlopen("https://www.google.com")).title.string,
  }
}
    
def createAllDayEvent(title, date, description, source):
    try:
        sourcetitle = BeautifulSoup(urllib2.urlopen(source)).title.string
    except:
        sourcetitle = ''
    return {
  'summary': title,
  'location': '',
  'description': description,
  'start': {
    'date': date,
    'timeZone': '',
  },
  'end': {
    'date': date,
    'timeZone': '',
  },
  'recurrence': [],
  'attendees': [],
  'reminders': {
    'useDefault': True,
    'overrides': [],
  },
  "source": {
    "url": source,
    "title": sourcetitle,
  }
}

def addEvent(title, eventtime, duration=None, description='', source=''):
    if duration is not None:
        starttimetext = eventtime.isoformat() + 'Z'
        endtimetext = (eventtime+duration).isoformat() + 'Z'
        event = createEvent(title, starttimetext, endtimetext, description, source)
    else:
        datetext = eventtime.strftime("%Y-%m-%d")
        event = createAllDayEvent(title, datetext, description, source)
    #print service.calendarList().list(pageToken=None).execute()
    if CALENDAR_ID is not None:
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    else:
        raise TypeError("Call setCalendarID before trying to add an event!")
    
def getEvents(timeMin, timeMax):
    if CALENDAR_ID is not None:
        pass
    else:
        raise TypeError("Call setCalendarID before trying to add an event!")
    page_token = None
    events = []
    while True:
        eventsResult = service.events().list(calendarId=CALENDAR_ID, timeMin=timeMin.isoformat() + 'Z', timeMax=timeMax.isoformat() + 'Z', maxResults=2500).execute()
        events.extend( eventsResult.get('items', []) )
        page_token = eventsResult.get('nextPageToken')
        if not page_token: break
    return events