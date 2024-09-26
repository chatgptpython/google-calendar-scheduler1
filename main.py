import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Haal de Bearer token en HubSpot API token op uit de environment
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")

# Functie om een specifieke ticket op te halen van HubSpot
def get_hubspot_ticket(ticket_id):
    url = f"https://api.hubapi.com/crm-objects/v1/objects/tickets/{ticket_id}"
    params = {
        "properties": ["subject", "content", "created_by", "hs_pipeline", "hs_pipeline_stage"]
    }
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"HubSpot API Error: {response.status_code}"}

# Endpoint om een HubSpot-ticket op te halen via POST
@app.route('/api/get_ticket_from_chatbot', methods=['POST'])
def post_ticket_from_chatbot():
    # Verifieer de bearer token van de klant
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Geen of ongeldige Authorization header"}), 401

    token = auth_header.split(" ")[1]
    if token != BEARER_TOKEN:
        return jsonify({"error": "Ongeldige bearer token"}), 403

    # Verkrijg de JSON data van de request (moet in de body staan, niet in de URL)
    data = request.json
    if 'ticket_id' not in data:
        return jsonify({"error": "Geen ticket ID meegegeven"}), 400

    ticket_id = data['ticket_id']
    ticket_data = get_hubspot_ticket(ticket_id)

    return jsonify(ticket_data)

if __name__ == '__main__':
    app.run(debug=True)
