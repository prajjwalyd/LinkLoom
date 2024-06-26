from app import db

class URL(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.Text, unique=True, nullable=False)
    custom_url = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    expires_at = db.Column(db.TIMESTAMP)

class Analytics(db.Model):
    __tablename__ = 'analytics'
    id = db.Column(db.Integer, primary_key=True)
    short_url_id = db.Column(db.Integer, db.ForeignKey('urls.id'), nullable=False)
    click_count = db.Column(db.Integer, default=0)
    last_clicked = db.Column(db.TIMESTAMP)
    # Define relationship
    short_url = db.relationship('URL', backref=db.backref('analytics', lazy=True))
