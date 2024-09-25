import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Calendar API-scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_credentials():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load environment variables for Google OAuth2 credentials
            client_id = os.getenv('CLIENT_ID')
            client_secret = os.getenv('CLIENT_SECRET')
            redirect_uri = os.getenv('REDIRECT_URI')
            auth_uri = os.getenv('AUTH_URI')
            token_uri = os.getenv('TOKEN_URI')

            flow = InstalledAppFlow.from_client_config({
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": auth_uri,
                    "token_uri": token_uri,
                    "redirect_uris": [redirect_uri]
                }
            }, SCOPES)

            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Function to create a Google Calendar event
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

# Function to schedule an appointment from JSON
def schedule_appointment_from_json(json_payload):
    data = json.loads(json_payload)

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    timezone = data['start']['timeZone']

    create_google_calendar_event(start_datetime, end_datetime, summary, timezone)

# Example JSON data
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
  "summary": "Meeting with Max"
}
'''

# Call the function to schedule the appointment
schedule_appointment_from_json(example_json)
