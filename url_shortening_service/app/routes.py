from flask import request, jsonify, redirect, url_for
from app import app, db
from app.models import URL, Analytics
import random
import string
import redis
import json

# Redis configuration
redis_host = "redis"
redis_port = 6379
redis_channel = "url_channel"

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    long_url = request.json.get('long_url')
    custom_url = request.json.get('custom_url')

    if not long_url:
        return jsonify({'error': 'Long URL is required'}), 400

    if custom_url:
        existing_url = URL.query.filter_by(short_url=custom_url).first()
        if existing_url:
            return jsonify({'error': 'Custom URL already exists'}), 400
        short_url = custom_url
    else:
        short_url = generate_short_url()

    # Create new URL record
    new_url = URL(long_url=long_url, short_url=short_url)
    db.session.add(new_url)
    db.session.commit()

    # Publish to Redis
    redis_data = {
        'long_url': long_url,
        'short_url': short_url
    }
    redis_client.publish(redis_channel, json.dumps(redis_data))

    return jsonify({
        'short_url': short_url,
        'long_url': long_url
    }), 201
