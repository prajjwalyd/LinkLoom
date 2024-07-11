from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@my-postgresql:5432/analytics-db'

try:
    db = SQLAlchemy(app)
    logger.info("Successfully connected to the database")
except Exception as e:
    logger.error("Error connecting to the database: %s", e)
    raise

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    referrer = db.Column(db.String, nullable=True)

@app.route('/log', methods=['POST'])
def log_access():
    data = request.get_json()
    url = data['url']
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    referrer = request.headers.get('Referer')
    
    entry = Analytics(url=url, ip_address=ip_address, user_agent=user_agent, referrer=referrer)
    db.session.add(entry)
    db.session.commit()
    return 'Logged', 200

@app.route('/<short_url>/analytics', methods=['GET'])
def get_analytics(short_url):
    entries = Analytics.query.filter_by(url=short_url).all()
    result = [{
        'access_time': entry.access_time,
        'ip_address': entry.ip_address,
        'user_agent': entry.user_agent,
        'referrer': entry.referrer
    } for entry in entries]
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5003, host='0.0.0.0')
