import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from flask import Flask

app = Flask(__name__)

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Load credentials from the environment variable
def get_credentials():
    with open('/etc/secrets/google-credentials.json') as f:
        service_account_info = json.load(f)
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

# Example route to test the Flask app
@app.route('/')
def index():
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
    schedule_appointment_from_json(example_json)
    return "Event scheduled successfully!"

if __name__ == '__main__':
    app.run(debug=True)
