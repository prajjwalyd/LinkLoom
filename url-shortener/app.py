from flask import Flask, request, jsonify, abort
import random
import string

app = Flask(__name__)

# Function to generate a random short URL
def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'long_url' not in data:
        abort(400, description="Invalid request: 'long_url' is required")

    long_url = data['long_url']
    custom_url = data.get('custom_url')

    if custom_url:
        short_url = custom_url
    else:
        short_url = generate_short_url()
    
    return jsonify({'short_url': short_url, 'long_url': long_url})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
