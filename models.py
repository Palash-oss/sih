from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    language = db.Column(db.String(10), default='en')
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy=True, cascade='all, delete-orphan')
    vaccination_reminders = db.relationship('VaccinationReminder', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'name': self.name,
            'age': self.age,
            'language': self.language,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'whatsapp' or 'sms'
    incoming_message = db.Column(db.Text, nullable=False)
    outgoing_message = db.Column(db.Text)
    detected_language = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message_type': self.message_type,
            'incoming_message': self.incoming_message,
            'outgoing_message': self.outgoing_message,
            'detected_language': self.detected_language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class VaccinationReminder(db.Model):
    __tablename__ = 'vaccination_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_sent_at = db.Column(db.DateTime)
    age_group = db.Column(db.String(20))  # 'child', 'adult'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vaccine_name': self.vaccine_name,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'reminder_sent': self.reminder_sent,
            'reminder_sent_at': self.reminder_sent_at.isoformat() if self.reminder_sent_at else None,
            'age_group': self.age_group,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OutbreakAlert(db.Model):
    __tablename__ = 'outbreak_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(100), nullable=False)
    alert_message = db.Column(db.Text, nullable=False)
    affected_locations = db.Column(db.Text)  # JSON string of locations
    severity_level = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def get_affected_locations(self):
        try:
            return json.loads(self.affected_locations) if self.affected_locations else []
        except json.JSONDecodeError:
            return []
    
    def set_affected_locations(self, locations):
        self.affected_locations = json.dumps(locations)
    
    def to_dict(self):
        return {
            'id': self.id,
            'disease_name': self.disease_name,
            'alert_message': self.alert_message,
            'affected_locations': self.get_affected_locations(),
            'severity_level': self.severity_level,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class HealthStatistics(db.Model):
    __tablename__ = 'health_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    total_messages = db.Column(db.Integer, default=0)
    whatsapp_messages = db.Column(db.Integer, default=0)
    sms_messages = db.Column(db.Integer, default=0)
    unique_users = db.Column(db.Integer, default=0)
    symptom_queries = db.Column(db.Integer, default=0)
    vaccination_queries = db.Column(db.Integer, default=0)
    prevention_queries = db.Column(db.Integer, default=0)
    emergency_queries = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_messages': self.total_messages,
            'whatsapp_messages': self.whatsapp_messages,
            'sms_messages': self.sms_messages,
            'unique_users': self.unique_users,
            'symptom_queries': self.symptom_queries,
            'vaccination_queries': self.vaccination_queries,
            'prevention_queries': self.prevention_queries,
            'emergency_queries': self.emergency_queries
        }

def init_db(app):
    """Initialize database with app context."""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")