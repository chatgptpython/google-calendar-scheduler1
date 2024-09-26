import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Je Bearer Token (vervang YOUR_BEARER_TOKEN met je daadwerkelijke token)
bearer_token = "eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzI3MzYwMjU0LCJqdGkiOiJhYzFjNGQ1Ny0yZjI5LTQ3NjEtOTZkMS0xNGZiM2U3MGE3OGQiLCJ1c2VyX3V1aWQiOiJhYTdiNGZjMC00NTY4LTQzZDktOWMwYy02NDVkYzFkNDE5ZDgifQ.6Vzfjvcw9JnihzB1W8uGaFsmegEjDSgrMS4c4Ph0I8AS-eqYTqB0IGPxiceBS09o0BQbbGkP-d1vGeNQ4N5HcQ"

# Functie om een afspraak te maken via de Calendly API
@app.route('/create_event', methods=['POST'])
def create_event():
    # Ontvang de JSON-data van de GPT-trainer chatbot
    data = request.json

    # Controleer of de benodigde gegevens aanwezig zijn
    if not all(key in data for key in ['start', 'end', 'summary', 'invitee_email']):
        return jsonify({"message": "Ontbrekende vereiste velden."}), 400

    start_time = data['start']['dateTime']
    end_time = data['end']['dateTime']
    event_name = data['summary']
    invitee_email = data['invitee_email']
    time_zone = data['start']['timeZone']

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
                "email": invitee_email,
                "name": "Invitee Name"  # Voeg een standaardnaam toe
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
