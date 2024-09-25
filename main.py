import datetime
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from flask import Flask, request, jsonify

# Flask app maken
app = Flask(__name__)

# Google Calendar API-scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Laad de client secret JSON van omgevingsvariabelen
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Functie om een afspraak in te plannen
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
    return event_result['htmlLink']

# Endpoint om JSON-gegevens te verwerken en de afspraak te plannen
@app.route('/schedule', methods=['POST'])
def schedule_appointment_from_json():
    data = request.get_json()

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    timezone = data['start']['timeZone']

    event_link = create_google_calendar_event(start_datetime, end_datetime, summary, timezone)
    return jsonify({"message": "Event created successfully", "event_link": event_link})

# Start de app
@app.route('/')
def home():
    return "Google Calendar Scheduling Assistant is running"

if __name__ == '__main__':
    app.run(debug=True)
