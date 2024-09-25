import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from flask import Flask, request, jsonify

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
    return event_result['htmlLink']

# Function to schedule an appointment from JSON payload
def schedule_appointment_from_json(json_payload):
    data = json.loads(json_payload)

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    timezone = data['start']['timeZone']

    return create_google_calendar_event(start_datetime, end_datetime, summary, timezone)

# API route to create a new event
@app.route('/create_event', methods=['POST'])
def create_event():
    try:
        json_payload = request.get_json()
        event_link = schedule_appointment_from_json(json.dumps(json_payload))
        return jsonify({"status": "Event created", "event_link": event_link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Example route to test the Flask app
@app.route('/')
def index():
    return "Welcome to the Google Calendar Scheduler API!"

if __name__ == '__main__':
    app.run(debug=True)
