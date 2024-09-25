from flask import Flask, request, jsonify
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

app = Flask(__name__)

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Function to get Google credentials
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
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
    return event_result['htmlLink']

# Route to handle scheduling requests
@app.route('/schedule', methods=['POST'])
def schedule_event():
    try:
        data = request.json  # Get JSON payload from POST request
        start_datetime = data['start']['dateTime']
        end_datetime = data['end']['dateTime']
        summary = data['summary']
        timezone = data['start'].get('timeZone', 'Europe/Amsterdam')
        
        # Create event in Google Calendar
        event_link = create_google_calendar_event(start_datetime, end_datetime, summary, timezone)
        
        # Return success response
        return jsonify({"message": "Event created successfully", "event_link": event_link}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
