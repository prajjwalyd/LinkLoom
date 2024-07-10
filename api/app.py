from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
import requests
import io

app = Flask(__name__)

# client = MongoClient('mongodb://root:example@mongo_db:27017/url_db')
client = MongoClient(host='test_mongodb', port=27017, username='root', password='example', authSource="admin") 
db = client.url_db

@app.route('/create', methods=['POST'])
def create_entry():
    data = request.get_json()
    long_url = data['long_url']
    
    # Generate short URL
    response = requests.post('http://url_shortener:5001/shorten', json={'long_url': long_url})
    short_url = response.json()['short_url']
    
    # Generate QR Code
    qr_response = requests.get(f'http://qr_code_generator:5002/generate_qr', params={'url': long_url})
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
    requests.post('http://analytics:5003/log', json={'url': entry['long_url']})
    
    return jsonify({'long_url': entry['long_url']})

@app.route('/qr/<short_url>', methods=['GET'])
def get_qr_code(short_url):
    entry = db.entries.find_one({'short_url': short_url})
    if not entry:
        return 'QR Code not found', 404
    
    # Log access
    requests.post('http://analytics:5003/log', json={'url': entry['long_url']})
    
    return send_file(io.BytesIO(entry['qr_code']), mimetype='image/png')

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
