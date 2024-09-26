import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Je Calendly OAuth Client gegevens
client_id = "DSCKFx4aSa5rXgSRstTEkxZvcU96lLCifce1FMH1HY8"  # Nieuwe Client ID
client_secret = "EClIUPliBmdWcb5szaZ9bLOK2Tzg5fSxbpZScraSgOs"  # Nieuwe Client Secret
redirect_uri = "https://google-calendar-scheduler1.onrender.com"

# Refresh Token (verkregen via de OAuth flow)
refresh_token = "YOUR_REFRESH_TOKEN"

# Variabele voor de Bearer Token en de tijd dat deze geldig is
bearer_token = None
expires_in = 3600  # Standaard vervaltijd van 1 uur voor de Bearer Token

# Functie om de Bearer Token te vernieuwen met de Refresh Token
def refresh_bearer_token():
    global bearer_token, expires_in
    url = "https://auth.calendly.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        tokens = response.json()
        bearer_token = tokens['access_token']
        expires_in = tokens['expires_in']
        print("Nieuwe Bearer Token verkregen:", bearer_token)
        return expires_in  # Retourneer de nieuwe vervaltijd in seconden
    else:
        print("Kon Bearer Token niet vernieuwen:", response.status_code, response.text)
        return None

# Functie om de afspraak aan te maken via de Calendly API
@app.route('/create_event', methods=['POST'])
def create_event():
    # Ontvang de JSON-data van de GPT-trainer chatbot
    data = request.json
    start_time = data['start_time']
    end_time = data['end_time']
    event_name = data['name']
    invitee_email = data['invitee_email']
    time_zone = data.get('time_zone', 'Europe/Amsterdam')  # Standaard naar Europe/Amsterdam als geen tijdzone is opgegeven

    # Controleer of de Bearer Token moet worden vernieuwd
    if bearer_token is None or expires_in < 300:  # Vernieuw de token als deze binnen 5 minuten verloopt
        refresh_bearer_token()

    # API URL voor het maken van een afspraak in Calendly
    calendly_api_url = "https://api.calendly.com/scheduled_events"

    # Gegevens voor de afspraak (payload)
    event_data = {
        "start_time": start_time,
        "end_time": end_time,
        "name": event_name,
        "time_zone": time_zone,
        "invitees": [
            {
                "email": invitee_email,  # E-mail van de genodigde
                "name": "Invitee Name"   # Naam van de genodigde
            }
        ]
    }

    # Voeg de Bearer Token toe aan de headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Verstuur het POST-verzoek naar de Calendly API
    response = requests.post(calendly_api_url, headers=headers, json=event_data)

    if response.status_code == 201:
        print("Afspraak succesvol ingepland!")
        return jsonify({"message": "Afspraak succesvol ingepland", "data": response.json()}), 201  # Succesvolle respons terug naar GPT-trainer
    else:
        print(f"Fout bij het inplannen van de afspraak: {response.status_code}")
        return jsonify({"message": "Fout bij het inplannen van de afspraak", "error": response.text}), 400

# De server opstarten
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
