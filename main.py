import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import Flask, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a_random_secret_key")

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
REDIRECT_URI = "https://jouw-redirect-url.com/callback"  # Pas dit aan naar jouw URL

# Start OAuth autorisatieproces
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(authorization_url)

# OAuth callback endpoint
@app.route('/callback')
def oauth2callback():
    state = session['state']
    
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('calendar_event'))

# Functie om een Google Calendar event in te plannen
@app.route('/calendar_event')
def calendar_event():
    if 'credentials' not in session:
        return redirect('authorize')

    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': 'Test Event',
        'start': {
            'dateTime': '2024-09-26T09:00:00',
            'timeZone': 'Europe/Amsterdam',
        },
        'end': {
            'dateTime': '2024-09-26T09:30:00',
            'timeZone': 'Europe/Amsterdam',
        }
    }

    event_result = service.events().insert(calendarId='primary', body=event).execute()

    return f"Event created: {event_result.get('htmlLink')}"

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    app.run(debug=True)
