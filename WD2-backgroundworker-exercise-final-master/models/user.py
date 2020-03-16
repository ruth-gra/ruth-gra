from models.settings import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)  # a username must be unique!
    email_address = db.Column(db.String, unique=True)  # email must be unique!
    password_hash = db.Column(db.String)
    session_token = db.Column(db.String)

    verified = db.Column(db.Boolean, default=False)  # has user already verified email address?
    verification_token = db.Column(db.String)

    created = db.Column(db.DateTime, default=datetime.utcnow)
