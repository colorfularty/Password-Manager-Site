from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Password(db.Model):
    username = db.Column(db.String(150), primary_key=True)
    password_name = db.Column(db.String(150), primary_key=True)
    password_value = db.Column(db.String(150))