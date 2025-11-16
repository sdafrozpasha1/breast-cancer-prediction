"""
Database module for production use
Replace in-memory storage with actual database
"""

from datetime import datetime
import json
import os

class Database:
    """Simple file-based database for development"""
    
    def __init__(self, db_path='data'):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        
        self.users_file = os.path.join(db_path, 'users.json')
        self.predictions_file = os.path.join(db_path, 'predictions.json')
        
        # Initialize files if they don't exist
        if not os.path.exists(self.users_file):
            self._save_json(self.users_file, {})
        if not os.path.exists(self.predictions_file):
            self._save_json(self.predictions_file, {})
    
    def _load_json(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    # User operations
    def get_user(self, email):
        users = self._load_json(self.users_file)
        return users.get(email)
    
    def create_user(self, email, user_data):
        users = self._load_json(self.users_file)
        users[email] = user_data
        self._save_json(self.users_file, users)
    
    def user_exists(self, email):
        users = self._load_json(self.users_file)
        return email in users
    
    # Prediction operations
    def save_prediction(self, user_email, prediction_data):
        predictions = self._load_json(self.predictions_file)
        
        if user_email not in predictions:
            predictions[user_email] = []
        
        predictions[user_email].append(prediction_data)
        self._save_json(self.predictions_file, predictions)
    
    def get_user_predictions(self, user_email):
        predictions = self._load_json(self.predictions_file)
        return predictions.get(user_email, [])
    
    def get_prediction_count(self, user_email):
        predictions = self.get_user_predictions(user_email)
        return len(predictions)

# For production, use SQLAlchemy with PostgreSQL
"""
Example PostgreSQL setup:

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    predictions = db.relationship('Prediction', backref='user', lazy=True)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)
    input_data = db.Column(db.JSON, nullable=False)
    result_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""
