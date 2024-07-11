from flask import Flask, request, jsonify, send_file, redirect
from pymongo import MongoClient, errors
import requests
import io
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

try:
    client = MongoClient('mongodb://root:example@my-mongo-mongodb:27017/url_db')
    db = client.url_db
    logging.info("Connected to MongoDB successfully.")
except errors.ServerSelectionTimeoutError as err:
    logging.error("Failed to connect to MongoDB: %s", err)



# client = MongoClient(host='testmongodb', port=27017, username='root', password='example', authSource="admin")
# db = client.url_db

@app.route('/create', methods=['POST'])
def create_entry():
    data = request.get_json()
    long_url = data['long_url']
    custom_url = data.get('custom_url')
    generate_qr = data.get('generate_qr', False)
    
    # Check if custom URL already exists
    if custom_url and db.entries.find_one({'short_url': custom_url}):
        return jsonify({'error': 'Custom URL already exists'}), 400
    
    # Generate short URL
    response = requests.post('http://url-shortener:5001/shorten', json={'long_url': long_url, 'custom_url': custom_url})
    short_url = response.json()['short_url']
    
    # Optionally generate QR Code
    qr_code = None
    if generate_qr:
        qr_response = requests.get(f'http://qr-code-generator:5002/generate_qr', params={'url': long_url})
        qr_code = qr_response.content
    
    # Save to MongoDB
    db.entries.insert_one({'long_url': long_url, 'short_url': short_url, 'qr_code': qr_code})
    
    return jsonify({'short_url': short_url, 'long_url': long_url})

@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    entry = db.entries.find_one({'short_url': short_url})
    if not entry:
        return 'URL not found', 404
    
    # Log access
    requests.post('http://analytics:5003/log', json={'url': short_url})
    
    return redirect(entry['long_url'])

@app.route('/qr/<short_url>', methods=['GET'])
def get_qr_code(short_url):
    entry = db.entries.find_one({'short_url': short_url})
    if not entry or not entry['qr_code']:
        return 'QR Code not found', 404
    
    return send_file(io.BytesIO(entry['qr_code']), mimetype='image/png')

@app.route('/<short_url>/analytics', methods=['GET'])
def get_analytics(short_url):
    entry = db.entries.find_one({'short_url': short_url})
    if not entry:
        return 'URL not found', 404
    
    analytics_response = requests.get(f'http://analytics:5003/{short_url}/analytics')
    if analytics_response.status_code != 200:
        return 'Error fetching analytics', analytics_response.status_code
    
    return jsonify(analytics_response.json())

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
