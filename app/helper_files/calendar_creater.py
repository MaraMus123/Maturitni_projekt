from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle


SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google_calendar():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            
            flow = InstalledAppFlow.from_client_secrets_file('/app/credentials/client_secret_calendar.json', SCOPES)
            creds = flow.run_console()  
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_new_events(service, event_list):
    for event in event_list:
        calendar_id = "64952e8c1a7313576772a16d374474b3995188aea30825d9d168f11cb5f0f25e@group.calendar.google.com"
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

def create_calendar(service, calendar_name):
    calendar = {
        'summary': calendar_name,
        'timeZone': 'Europe/Berlin', 
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    print(f"Calendar created: {created_calendar['id']}")
    return created_calendar['id']

def calendar_add_events(event_list):
    service = authenticate_google_calendar()
    create_new_events(service, event_list)
    
    return "All the events successfully created!"

    
