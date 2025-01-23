from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle


SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google_calendar():
    creds = None

    if os.path.exists('/app/credentials/token.pickle'):
        with open('/app/credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    else:
        raise FileNotFoundError("Token not found")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:

            flow = InstalledAppFlow.from_client_secrets_file('/app/credentials/client_secret_calendar_api.json', SCOPES)
            creds = flow.run_console()

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def create_new_events(service, event_list):
    global calendar_id
    calendar_id = "64952e8c1a7313576772a16d374474b3995188aea30825d9d168f11cb5f0f25e@group.calendar.google.com"
    clear_calendar(service, calendar_id)
    x = 0
    for event in event_list:
        print(f"Creating event: {event['start']['date']} - {event['summary']}")
        event = service.events().insert(calendarId=calendar_id, body=event).execute()

def create_calendar(service, calendar_name):
    calendar = {
        'summary': calendar_name,
        'timeZone': 'Europe/Berlin',
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    print(f"Calendar created: {created_calendar['id']}")
    return created_calendar['id']

def clear_calendar(service, calendar_id):
    try:
        # Retrieve all events
        events = service.events().list(calendarId=calendar_id).execute()
        for event in events.get('items', []):
            # Delete each event
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            print(f"Deleted event: {event.get('summary', 'No title')}")
        print(f"All events deleted from calendar with ID: {calendar_id}")
    except Exception as e:
        print(f"An error occurred: {e}")

def calendar_add_events(event_list):
    global service
    service = authenticate_google_calendar()
    create_new_events(service, event_list)

    return "All the events successfully created!"


