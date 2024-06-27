from flask import request, jsonify
from app import app, db
from app.models import URL
import random
import string
import redis
import json


# postgres is kinda useless now

# Redis configuration
redis_host = "redis"
redis_port = 6379
redis_stream = "url_stream"

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

    # Publish to Redis Stream
    redis_data = {
        'data': json.dumps({
            'long_url': long_url,
            'short_url': short_url
        })
    }
    redis_client.xadd(redis_stream, redis_data)

    return jsonify({
        'short_url': short_url,
        'long_url': long_url
    }), 201
