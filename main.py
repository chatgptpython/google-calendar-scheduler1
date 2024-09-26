from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Statische lijst met 10 orders, inclusief verzonnen barcodes
orders = [
    {"order_number": "10001", "customer": "John Doe", "barcode": "123456789012"},
    {"order_number": "10002", "customer": "Jane Smith", "barcode": "234567890123"},
    {"order_number": "10003", "customer": "Alice Johnson", "barcode": "345678901234"},
    {"order_number": "10004", "customer": "Bob Brown", "barcode": "456789012345"},
    {"order_number": "10005", "customer": "Charlie White", "barcode": "567890123456"},
    {"order_number": "10006", "customer": "Daisy Black", "barcode": "678901234567"},
    {"order_number": "10007", "customer": "Evan Green", "barcode": "789012345678"},
    {"order_number": "10008", "customer": "Fiona Blue", "barcode": "890123456789"},
    {"order_number": "10009", "customer": "George Yellow", "barcode": "901234567890"},
    {"order_number": "10010", "customer": "Hannah Purple", "barcode": "012345678901"},
]

# Bearer token voor verificatie
BEARER_TOKEN = "abc123securetoken"

# Functie om bearer token te verifiëren
def verify_token(token):
    return token == BEARER_TOKEN

# Endpoint om een specifieke order op te halen via POST
@app.route('/api/get_order', methods=['POST'])
def get_order_post():
    # Verifieer de bearer token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Geen of ongeldige Authorization header"}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({"error": "Ongeldige bearer token"}), 403

    # Verkrijg de JSON data van de request
    data = request.json
    if 'order_number' not in data:
        return jsonify({"error": "Geen ordernummer meegegeven"}), 400

    order_number = data['order_number']

    # Zoek naar het ordernummer in de lijst
    order = next((order for order in orders if order["order_number"] == order_number), None)

    if order:
        return jsonify(order)
    else:
        return jsonify({"error": "Order niet gevonden"}), 404

# Endpoint om een specifieke order op te halen via GET met query parameters
@app.route('/api/order_tracker', methods=['GET'])
def get_order_get():
    # Verifieer de bearer token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Geen of ongeldige Authorization header"}), 401

    token = auth_header.split(" ")[1]
    if not verify_token(token):
        return jsonify({"error": "Ongeldige bearer token"}), 403

    # Haal het ordernummer op uit de query string
    order_number = request.args.get('order_number')
    if not order_number:
        return jsonify({"error": "Geen ordernummer meegegeven"}), 400

    # Zoek naar het ordernummer in de lijst
    order = next((order for order in orders if order["order_number"] == order_number), None)

    if order:
        return jsonify(order)
    else:
        return jsonify({"error": "Order niet gevonden"}), 404

if __name__ == '__main__':
    app.run(debug=True)
