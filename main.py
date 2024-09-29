from flask import Flask, jsonify, request
import logging

# Configuratie van logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Endpoint om de binnenkomende JSON te testen
@app.route('/api/test_json', methods=['POST'])
def test_json():
    # Verkrijg de JSON data van de request
    data = request.json
    logging.debug(f"Ontvangen JSON data: {data}")

    # Terugsturen van de ontvangen data als response
    return jsonify({"received_data": data}), 200

if __name__ == '__main__':
    app.run(debug=True)
