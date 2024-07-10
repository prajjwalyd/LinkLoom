from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@analytics_db:5432/analytics_db'
db = SQLAlchemy(app)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    access_time = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/log', methods=['POST'])
def log_access():
    data = request.get_json()
    url = data['url']
    entry = Analytics(url=url)
    db.session.add(entry)
    db.session.commit()
    return 'Logged', 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5003, host='0.0.0.0')
