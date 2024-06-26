from flask import request, jsonify, redirect, url_for
from app import app, db
from app.models import URL, Analytics
import random
import string

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

    return jsonify({
        'short_url': short_url,
        'long_url': long_url
    }), 201

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first()
    if url:
        # Update analytics (click count and last clicked time)
        analytics = Analytics.query.filter_by(short_url_id=url.id).first()
        if analytics:
            analytics.click_count += 1
            analytics.last_clicked = db.func.current_timestamp()
        else:
            new_analytics = Analytics(short_url_id=url.id, click_count=1, last_clicked=db.func.current_timestamp())
            db.session.add(new_analytics)
        db.session.commit()
        return redirect(url.long_url)
    else:
        return jsonify({'error': 'Short URL not found'}), 404
