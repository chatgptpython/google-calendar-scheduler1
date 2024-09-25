import datetime
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Calendar API-scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Haal de environment variables op
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
AUTH_URI = os.getenv("GOOGLE_AUTH_URI")
TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
AUTH_PROVIDER_CERT_URL = os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL")
REDIRECT_URIS = [os.getenv("GOOGLE_REDIRECT_URIS")]

# Maak het credentials object aan op basis van environment variables
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # OAuth flow instellen met environment variables
            flow = InstalledAppFlow.from_client_config({
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "project_id": PROJECT_ID,
                    "auth_uri": AUTH_URI,
                    "token_uri": TOKEN_URI,
                    "auth_provider_x509_cert_url": AUTH_PROVIDER_CERT_URL,
                    "redirect_uris": REDIRECT_URIS
                }
            }, SCOPES)
            creds = flow.run_local_server(port=0)
        # Sla de credentials op in 'token.json'
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Functie om een afspraak in Google Calendar in te plannen
def create_google_calendar_event(start_datetime, end_datetime, summary, timezone="Europe/Amsterdam"):
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_datetime,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': timezone,
        }
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event_result['htmlLink']}")

# Functie om JSON-gegevens te verwerken en de afspraak in te plannen
def schedule_appointment_from_json(json_payload):
    data = json.loads(json_payload)

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    timezone = data['start']['timeZone']  # Gebruik dezelfde tijdzone voor start en eind

    create_google_calendar_event(start_datetime, end_datetime, summary, timezone)

# Voorbeeld-JSON-data
example_json = '''
{
  "start": {
    "dateTime": "2024-09-26T09:00:00",
    "timeZone": "Europe/Amsterdam"
  },
  "end": {
    "dateTime": "2024-09-26T09:30:00",
    "timeZone": "Europe/Amsterdam"
  },
  "summary": "Mesten"
}
'''

# Voer de functie uit om de afspraak in te plannen
schedule_appointment_from_json(example_json)
