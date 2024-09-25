import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Function to get credentials using the OAuth2 flow (offline method)
def get_credentials():
    creds = None
    token_file = 'token.json'
    
    # Check if we have previously saved credentials
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # If credentials are invalid or don't exist, start the OAuth2 flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Initialize OAuth2 flow with client info from environment variables
            flow = InstalledAppFlow.from_client_config({
                "web": {
                    "client_id": os.getenv('CLIENT_ID'),
                    "project_id": os.getenv('PROJECT_ID'),
                    "auth_uri": os.getenv('AUTH_URI'),
                    "token_uri": os.getenv('TOKEN_URI'),
                    "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
                    "client_secret": os.getenv('CLIENT_SECRET')
                }
            }, SCOPES)

            # Generate the authorization URL for the user to complete the flow
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # Output the URL for the user to manually complete the authorization
            print(f'Please go to this URL and authorize access: {auth_url}')
            
            # Get the authorization code from the user
            auth_code = input('Enter the authorization code: ')

            # Fetch the credentials using the authorization code
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
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
