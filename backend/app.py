from flask import Flask, request, jsonify, session
from flask_cors import CORS
from pymongo import MongoClient
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "default_secret")

# MongoDB for auth
mongo_client = MongoClient(os.getenv("MONGO_URI"))
mongo_db = mongo_client["sih"]
users_collection = mongo_db["users"]

# SQLite for health logs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_logs.db'
db = SQLAlchemy(app)

class HealthLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    event = db.Column(db.String(256), nullable=False)
    date = db.Column(db.String(32), nullable=False)

db.create_all()

# --- AUTH ROUTES (MongoDB) ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    phone = data.get('phone')
    aadhaar = data.get('aadhaar')
    if users_collection.find_one({'phone': phone}):
        return jsonify({'error': 'User already exists'}), 400
    otp = str(random.randint(100000, 999999))
    users_collection.insert_one({'phone': phone, 'aadhaar': aadhaar, 'otp': otp, 'verified': False})
    # In production, send OTP via SMS
    return jsonify({'message': 'OTP sent', 'otp': otp})

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    user = users_collection.find_one({'phone': phone})
    if user and user['otp'] == otp:
        users_collection.update_one({'phone': phone}, {'$set': {'verified': True}})
        session['user_id'] = str(user['_id'])
        return jsonify({'message': 'Verified', 'user_id': str(user['_id'])})
    return jsonify({'error': 'Invalid OTP'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    aadhaar = data.get('aadhaar')
    user = users_collection.find_one({'phone': phone, 'aadhaar': aadhaar, 'verified': True})
    if user:
        session['user_id'] = str(user['_id'])
        return jsonify({'message': 'Login successful', 'user_id': str(user['_id'])})
    return jsonify({'error': 'Invalid credentials'}), 400

# --- HEALTH LOG ROUTES (SQLite) ---

@app.route('/api/healthlog', methods=['POST'])
def log_health():
    data = request.json
    user_id = data.get('user_id')
    event = data.get('event')
    date = data.get('date')
    if not user_id or not event or not date:
        return jsonify({'error': 'Missing fields'}), 400
    log = HealthLog(user_id=user_id, event=event, date=date)
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Health event logged'})

@app.route('/api/healthlog/<user_id>', methods=['GET'])
def get_health_logs(user_id):
    logs = HealthLog.query.filter_by(user_id=user_id).all()
    return jsonify([{'event': l.event, 'date': l.date} for l in logs])

if __name__ == '__main__':
    app.run(debug=True)