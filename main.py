import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Load credentials from environment variables
def get_credentials():
    # Fetch Google OAuth2 service account credentials from environment variables
    service_account_info = {
        "type": os.getenv('GOOGLE_TYPE'),
        "project_id": os.getenv('GOOGLE_PROJECT_ID'),
        "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),  # Handle newlines
        "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
        "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL'),
        "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_CERT_URL')
    }

    # Create credentials object from the service account info
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    return credentials

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

# Function to schedule an appointment from JSON payload
def schedule_appointment_from_json(json_payload):
    data = json.loads(json_payload)

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    timezone = data['start']['timeZone']

    create_google_calendar_event(start_datetime, end_datetime, summary, timezone)

# Example JSON data to schedule an event
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
