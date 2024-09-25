import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Calendly API base URL
CALENDLY_API_URL = "https://api.calendly.com/scheduled_events"

# Function to create a Calendly event using the Calendly API
def create_calendly_event(start_datetime, end_datetime, summary, invitee_email):
    # Bearer token (vervang dit met de echte token of haal hem dynamisch op)
    bearer_token = os.getenv("CALENDLY_BEARER_TOKEN")  # Zorg dat dit in de omgevingsvariabelen staat

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    event_data = {
        "event": {
            "name": summary,
            "start_time": start_datetime,
            "end_time": end_datetime,
            "invitee": {
                "email": invitee_email
            }
        }
    }

    response = requests.post(CALENDLY_API_URL, headers=headers, json=event_data)

    if response.status_code == 201:
        return response.json().get('resource', {}).get('uri', 'No link available')
    else:
        raise Exception(f"Failed to create event: {response.text}")

# Function to schedule an appointment from JSON payload
def schedule_appointment_from_json(json_payload):
    data = json.loads(json_payload)

    start_datetime = data['start']['dateTime']
    end_datetime = data['end']['dateTime']
    summary = data['summary']
    invitee_email = data['invitee_email']  # Invitee email needs to be passed for Calendly

    return create_calendly_event(start_datetime, end_datetime, summary, invitee_email)

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
    return "Welcome to the Calendly Scheduler API!"

if __name__ == '__main__':
    app.run(debug=True)
