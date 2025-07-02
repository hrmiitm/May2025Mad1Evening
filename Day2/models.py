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