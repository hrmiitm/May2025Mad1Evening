# Database Schema
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    
    isUser = db.Column(db.Boolean, default=True)
    isCreator = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)

    # Relationship
    songs = db.relationship('Song', backref='user', lazy = True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    lyrics = db.Column(db.String, default='')
    duration = db.Column(db.Integer, default='')
    date = db.Column(db.String, default='')
    rating = db.Column(db.Integer, default='')

    isBlacklisted = db.Column(db.Boolean, default=False)

    # One user can create many songs, One(user)-Many(song)
    # Foreighn key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)