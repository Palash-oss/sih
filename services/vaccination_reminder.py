import schedule
import time
from datetime import datetime, date, timedelta
from threading import Thread
from models import db, User, VaccinationReminder
from twilio.rest import Client
from config import Config
import json
import logging

logger = logging.getLogger(__name__)

class VaccinationReminderService:
    def __init__(self, app):
        self.app = app
        self.twilio_client = None
        if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Load vaccination schedule from knowledge base
        self.vaccination_schedules = self._load_vaccination_schedules()
        
        # Schedule daily reminder check
        schedule.every().day.at(f"{Config.REMINDER_SCHEDULE_HOUR:02d}:00").do(self._check_and_send_reminders)
        
        # Start scheduler in a separate thread
        self.scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _load_vaccination_schedules(self):
        """Load vaccination schedules from knowledge base."""
        try:
            with open('data/health_knowledge_base.json', 'r') as f:
                data = json.load(f)
            return data.get('vaccination_schedules', {})
        except Exception as e:
            logger.error(f"Error loading vaccination schedules: {e}")
            return {}
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _check_and_send_reminders(self):
        """Check for due reminders and send them."""
        if not Config.ENABLE_VACCINATION_REMINDERS or not self.twilio_client:
            return
        
        with self.app.app_context():
            try:
                # Get reminders due today or overdue
                today = date.today()
                due_reminders = VaccinationReminder.query.filter(
                    VaccinationReminder.due_date <= today,
                    VaccinationReminder.reminder_sent == False
                ).all()
                
                for reminder in due_reminders:
                    self._send_reminder(reminder)
                    
            except Exception as e:
                logger.error(f"Error checking reminders: {e}")
    
    def _send_reminder(self, reminder: VaccinationReminder):
        """Send a vaccination reminder to the user."""
        try:
            user = reminder.user
            if not user or not user.phone_number:
                return
            
            # Create reminder message
            message = self._create_reminder_message(reminder, user.language or 'en')
            
            # Send WhatsApp message if possible, otherwise SMS
            try:
                # Try WhatsApp first
                self.twilio_client.messages.create(
                    body=message,
                    from_=Config.TWILIO_WHATSAPP_NUMBER,
                    to=f'whatsapp:{user.phone_number}'
                )
                logger.info(f"WhatsApp reminder sent to {user.phone_number}")
            except:
                # Fallback to SMS
                self.twilio_client.messages.create(
                    body=message,
                    from_=Config.TWILIO_PHONE_NUMBER,
                    to=user.phone_number
                )
                logger.info(f"SMS reminder sent to {user.phone_number}")
            
            # Mark reminder as sent
            reminder.reminder_sent = True
            reminder.reminder_sent_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending reminder to {reminder.user_id}: {e}")
    
    def _create_reminder_message(self, reminder: VaccinationReminder, language: str) -> str:
        """Create a reminder message in the user's language."""
        messages = {
            'en': {
                'reminder': f"🩹 VACCINATION REMINDER\n\nHello! This is a reminder that {reminder.vaccine_name} vaccination is due.",
                'overdue': f"⚠️ OVERDUE VACCINATION\n\nThe {reminder.vaccine_name} vaccination was due on {reminder.due_date.strftime('%d/%m/%Y')}. Please schedule an appointment.",
                'footer': "\n\nPlease consult your healthcare provider.\n\nFor emergencies, call 108."
            },
            'hi': {
                'reminder': f"🩹 टीकाकरण अनुस्मारक\n\nनमस्ते! यह एक अनुस्मारक है कि {reminder.vaccine_name} टीकाकरण का समय आ गया है।",
                'overdue': f"⚠️ लंबित टीकाकरण\n\n{reminder.vaccine_name} टीकाकरण {reminder.due_date.strftime('%d/%m/%Y')} को देय था। कृपया अपॉइंटमेंट बुक करें।",
                'footer': "\n\nकृपया अपने स्वास्थ्य सेवा प्रदाता से सलाह लें।\n\nआपातकाल के लिए 108 पर कॉल करें।"
            }
        }
        
        lang_messages = messages.get(language, messages['en'])
        
        today = date.today()
        if reminder.due_date < today:
            message = lang_messages['overdue']
        else:
            message = lang_messages['reminder']
        
        if reminder.notes:
            message += f"\n\nNote: {reminder.notes}"
        
        message += lang_messages['footer']
        return message
    
    def create_reminder(self, user_id: int, vaccine_name: str, due_date: date, 
                       age_group: str = None, notes: str = None) -> VaccinationReminder:
        """Create a new vaccination reminder."""
        with self.app.app_context():
            reminder = VaccinationReminder(
                user_id=user_id,
                vaccine_name=vaccine_name,
                due_date=due_date,
                age_group=age_group,
                notes=notes
            )
            
            db.session.add(reminder)
            db.session.commit()
            return reminder
    
    def create_reminders_for_child(self, user_id: int, birth_date: date):
        """Create all vaccination reminders for a child based on birth date."""
        child_schedule = self.vaccination_schedules.get('children', {})
        
        with self.app.app_context():
            for age_key, vaccines in child_schedule.items():
                due_date = self._calculate_due_date(birth_date, age_key)
                
                for vaccine in vaccines:
                    reminder = VaccinationReminder(
                        user_id=user_id,
                        vaccine_name=vaccine,
                        due_date=due_date,
                        age_group='child',
                        notes=f"Scheduled for {age_key.replace('_', ' ')}"
                    )
                    db.session.add(reminder)
            
            db.session.commit()
    
    def _calculate_due_date(self, birth_date: date, age_key: str) -> date:
        """Calculate due date based on birth date and age key."""
        if age_key == 'birth':
            return birth_date
        elif 'weeks' in age_key:
            weeks = int(age_key.split('_')[0])
            return birth_date + timedelta(weeks=weeks)
        elif 'months' in age_key:
            months = int(age_key.split('_')[0])
            # Approximate months as 30 days
            return birth_date + timedelta(days=months * 30)
        elif 'years' in age_key:
            if '4_6_years' in age_key:
                # Default to 4 years
                return birth_date + timedelta(days=4 * 365)
            else:
                years = int(age_key.split('_')[0])
                return birth_date + timedelta(days=years * 365)
        else:
            # Default to 1 year if can't parse
            return birth_date + timedelta(days=365)
    
    def get_upcoming_reminders(self, user_id: int, days_ahead: int = 30):
        """Get upcoming reminders for a user."""
        with self.app.app_context():
            end_date = date.today() + timedelta(days=days_ahead)
            reminders = VaccinationReminder.query.filter(
                VaccinationReminder.user_id == user_id,
                VaccinationReminder.due_date <= end_date,
                VaccinationReminder.reminder_sent == False
            ).order_by(VaccinationReminder.due_date).all()
            
            return [reminder.to_dict() for reminder in reminders]
    
    def mark_vaccination_completed(self, reminder_id: int):
        """Mark a vaccination as completed."""
        with self.app.app_context():
            reminder = VaccinationReminder.query.get(reminder_id)
            if reminder:
                reminder.reminder_sent = True
                reminder.reminder_sent_at = datetime.utcnow()
                reminder.notes = f"{reminder.notes or ''} - Completed"
                db.session.commit()
                return True
            return False
