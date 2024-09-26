import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Je Calendly OAuth Client gegevens
client_id = "DSCKFx4aSa5rXgSRstTEkxZvcU96lLCifce1FMH1HY8"  # Nieuwe Client ID
client_secret = "EClIUPliBmdWcb5szaZ9bLOK2Tzg5fSxbpZScraSgOs"  # Nieuwe Client Secret
redirect_uri = "https://google-calendar-scheduler1.onrender.com"
authorization_code = None  # Deze moet handmatig worden verkregen via de OAuth-stroom

# Variabelen voor tokens
access_token = None
refresh_token = None
expires_in = 3600  # Standaard vervaltijd van 1 uur voor de Bearer Token

# Functie om de Authorization Code om te wisselen voor de Access en Refresh Token
def exchange_code_for_tokens(authorization_code):
    global access_token, refresh_token, expires_in
    url = "https://auth.calendly.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        expires_in = tokens['expires_in']
        print("Tokens verkregen! Access Token:", access_token, "Refresh Token:", refresh_token)
        return True
    else:
        print("Kon de tokens niet verkrijgen:", response.status_code, response.text)
        return False

# Functie om de Bearer Token te vernieuwen met de Refresh Token
def refresh_bearer_token():
    global access_token, expires_in
    url = "https://auth.calendly.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        expires_in = tokens['expires_in']
        print("Nieuwe Bearer Token verkregen:", access_token)
        return expires_in  # Retourneer de nieuwe vervaltijd in seconden
    else:
        print("Kon Bearer Token niet vernieuwen:", response.status_code, response.text)
        return None

# Functie om de geldigheid van de Bearer Token te controleren (introspectie)
def introspect_token():
    global access_token
    url = "https://auth.calendly.com/oauth/introspect"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "token": access_token
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token_info = response.json()
        if token_info['active']:
            print("De Bearer Token is actief.")
            return True
        else:
            print("De Bearer Token is inactief.")
            return False
    else:
        print("Fout bij introspectie:", response.status_code, response.text)
        return False

# Functie om de afspraak aan te maken via de Calendly API
@app.route('/create_event', methods=['POST'])
def create_event():
    # Controleer of de Bearer Token moet worden vernieuwd
    if not introspect_token() or expires_in < 300:  # Vernieuw de token als deze binnen 5 minuten verloopt
        refresh_bearer_token()

    # Ontvang de JSON-data van de GPT-trainer chatbot
    data = request.json
    start_time = data['start']['dateTime']
    end_time = data['end']['dateTime']
    time_zone = data['start']['timeZone']
    event_name = data['summary']
    invitee_email = data.get('invitee_email', 'klant@example.com')  # Voeg standaard invitee_email toe als geen is opgegeven

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
        "Authorization": f"Bearer {access_token}",
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
    # Controleer of de Authorization Code al is ingesteld
    if authorization_code:
        # Verwissel de Authorization Code voor tokens als deze nog niet zijn ingesteld
        if not access_token or not refresh_token:
            if not exchange_code_for_tokens(authorization_code):
                print("Fout bij het verkrijgen van de tokens. Zorg ervoor dat de Authorization Code correct is.")
    app.run(host='0.0.0.0', port=5000)
