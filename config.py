import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Translate Configuration
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///healthcare_chatbot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Health API Configuration
    HEALTH_API_BASE_URL = os.getenv('HEALTH_API_BASE_URL')
    HEALTH_API_KEY = os.getenv('HEALTH_API_KEY')
    
    # Vaccination Reminder Configuration
    ENABLE_VACCINATION_REMINDERS = os.getenv('ENABLE_VACCINATION_REMINDERS', 'True').lower() == 'true'
    REMINDER_SCHEDULE_HOUR = int(os.getenv('REMINDER_SCHEDULE_HOUR', 9))
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'bn': 'Bengali',
        'te': 'Telugu',
        'ta': 'Tamil',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'mr': 'Marathi'
    }
    
    # Babel Configuration
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = SUPPORTED_LANGUAGES