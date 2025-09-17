from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from services.image_diagnosis_service import mock_image_classifier
from services.response_formatter import ResponseFormatter
from flask_cors import CORS
from flask_babel import Babel, gettext, ngettext, get_locale
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config import Config
from models import db, User, Message, VaccinationReminder, OutbreakAlert, HealthStatistics, init_db
from chatbot.health_bot import HealthChatbot
from datetime import datetime, date
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize Babel for internationalization
babel = Babel(app)

def get_locale():
    """Determine the best language for the user."""
    # Check if language is set in session
    if 'language' in session:
        return session['language']
    
    # Check if language is provided in URL parameter
    if request.args.get('lang'):
        return request.args.get('lang')
    
    # Check browser language preferences
    return request.accept_languages.best_match(Config.SUPPORTED_LANGUAGES.keys()) or 'en'

# Note: Locale selector will be handled manually in routes

# Initialize database
init_db(app)

# Initialize Twilio client
twilio_client = None
if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
    twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

# Initialize chatbot
health_bot = HealthChatbot()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive translation dictionaries for all supported languages
translations = {
    'hi': {  # Hindi
        'AI-Powered Healthcare Assistant': 'AI-संचालित स्वास्थ्य सहायक',
        'Features': 'सुविधाएं',
        'Test Bot': 'बॉट टेस्ट करें',
        'Dashboard': 'डैशबोर्ड',
        'Accessible healthcare information in your local language through WhatsApp and SMS. Get instant guidance on symptoms, prevention, and vaccination schedules.': 'WhatsApp और SMS के माध्यम से आपकी स्थानीय भाषा में सुलभ स्वास्थ्य जानकारी। लक्षणों, रोकथाम और टीकाकरण कार्यक्रम पर तत्काल मार्गदर्शन प्राप्त करें।',
        'Key Features': 'मुख्य सुविधाएं',
        'Comprehensive healthcare assistance at your fingertips': 'आपकी उंगलियों पर व्यापक स्वास्थ्य सहायता',
        'Multilingual Support': 'बहुभाषी समर्थन',
        'Available in Hindi, English, Bengali, Telugu, Tamil, and other regional languages': 'हिंदी, अंग्रेजी, बंगाली, तेलुगु, तमिल और अन्य क्षेत्रीय भाषाओं में उपलब्ध',
        'Symptom Analysis': 'लक्षण विश्लेषण',
        'Intelligent symptom recognition and disease information with prevention tips': 'बुद्धिमान लक्षण पहचान और रोकथाम सुझावों के साथ रोग जानकारी',
        'Vaccination Reminders': 'टीकाकरण अनुस्मारक',
        'Personalized vaccination schedules and automated reminders for all age groups': 'सभी आयु समूहों के लिए व्यक्तिगत टीकाकरण कार्यक्रम और स्वचालित अनुस्मारक',
        'Prevention Tips': 'रोकथाम सुझाव',
        'Evidence-based preventive health guidance for nutrition, exercise, and hygiene': 'पोषण, व्यायाम और स्वच्छता के लिए साक्ष्य-आधारित निवारक स्वास्थ्य मार्गदर्शन',
        'Emergency Contacts': 'आपातकालीन संपर्क',
        'Quick access to emergency numbers and health helplines': 'आपातकालीन नंबर और स्वास्थ्य हेल्पलाइन तक त्वरित पहुंच',
        'Outbreak Alerts': 'प्रकोप अलर्ट',
        'Real-time disease outbreak notifications and health advisories': 'वास्तविक समय रोग प्रकोप सूचनाएं और स्वास्थ्य सलाह',
        'Test the Chatbot': 'चैटबॉट का परीक्षण करें',
        'Try asking health-related questions below': 'नीचे स्वास्थ्य संबंधी प्रश्न पूछने का प्रयास करें',
        'Healthcare Assistant': 'स्वास्थ्य सहायक',
        'Hello! I\'m your healthcare assistant. I can help you with symptoms, prevention tips, vaccination schedules, and emergency contacts. What would you like to know?': 'नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। मैं आपकी लक्षणों, रोकथाम सुझावों, टीकाकरण कार्यक्रम और आपातकालीन संपर्कों में मदद कर सकता हूं। आप क्या जानना चाहते हैं?',
        'Type your health question...': 'अपना स्वास्थ्य प्रश्न टाइप करें...',
        'Total Users': 'कुल उपयोगकर्ता',
        'Messages Processed': 'संसाधित संदेश',
        'Supported Languages': 'समर्थित भाषाएं',
        'Availability': 'उपलब्धता',
        'AI Healthcare Chatbot': 'AI स्वास्थ्य चैटबॉट',
        'Making healthcare information accessible to all.': 'सभी के लिए स्वास्थ्य जानकारी को सुलभ बनाना।',
        'Built with': 'के साथ निर्मित',
        'for rural healthcare': 'ग्रामीण स्वास्थ्य सेवा के लिए',
        'Send "Hello" to get started': 'शुरू करने के लिए "Hello" भेजें',
        'Text your health questions': 'अपने स्वास्थ्य प्रश्न टेक्स्ट करें'
    },
    'bn': {  # Bengali
        'AI-Powered Healthcare Assistant': 'AI-চালিত স্বাস্থ্য সহায়ক',
        'Features': 'বৈশিষ্ট্য',
        'Test Bot': 'বট পরীক্ষা করুন',
        'Dashboard': 'ড্যাশবোর্ড',
        'Accessible healthcare information in your local language through WhatsApp and SMS. Get instant guidance on symptoms, prevention, and vaccination schedules.': 'WhatsApp এবং SMS এর মাধ্যমে আপনার স্থানীয় ভাষায় সহজলভ্য স্বাস্থ্য তথ্য। লক্ষণ, প্রতিরোধ এবং টিকাদান সময়সূচী সম্পর্কে তাত্ক্ষণিক নির্দেশনা পান।',
        'Key Features': 'মূল বৈশিষ্ট্য',
        'Comprehensive healthcare assistance at your fingertips': 'আপনার আঙুলের ডগায় ব্যাপক স্বাস্থ্য সহায়তা',
        'Multilingual Support': 'বহুভাষিক সমর্থন',
        'Available in Hindi, English, Bengali, Telugu, Tamil, and other regional languages': 'হিন্দি, ইংরেজি, বাংলা, তেলুগু, তামিল এবং অন্যান্য আঞ্চলিক ভাষায় উপলব্ধ',
        'Symptom Analysis': 'লক্ষণ বিশ্লেষণ',
        'Intelligent symptom recognition and disease information with prevention tips': 'প্রতিরোধ টিপস সহ বুদ্ধিমান লক্ষণ স্বীকৃতি এবং রোগের তথ্য',
        'Vaccination Reminders': 'টিকাদান অনুস্মারক',
        'Personalized vaccination schedules and automated reminders for all age groups': 'সব বয়সের জন্য ব্যক্তিগত টিকাদান সময়সূচী এবং স্বয়ংক্রিয় অনুস্মারক',
        'Prevention Tips': 'প্রতিরোধ টিপস',
        'Evidence-based preventive health guidance for nutrition, exercise, and hygiene': 'পুষ্টি, ব্যায়াম এবং স্বাস্থ্যবিধির জন্য প্রমাণ-ভিত্তিক প্রতিরোধমূলক স্বাস্থ্য নির্দেশনা',
        'Emergency Contacts': 'জরুরি যোগাযোগ',
        'Quick access to emergency numbers and health helplines': 'জরুরি নম্বর এবং স্বাস্থ্য হেল্পলাইনে দ্রুত অ্যাক্সেস',
        'Outbreak Alerts': 'প্রাদুর্ভাব সতর্কতা',
        'Real-time disease outbreak notifications and health advisories': 'রিয়েল-টাইম রোগ প্রাদুর্ভাব বিজ্ঞপ্তি এবং স্বাস্থ্য পরামর্শ',
        'Test the Chatbot': 'চ্যাটবট পরীক্ষা করুন',
        'Try asking health-related questions below': 'নীচে স্বাস্থ্য-সম্পর্কিত প্রশ্ন জিজ্ঞাসা করার চেষ্টা করুন',
        'Healthcare Assistant': 'স্বাস্থ্য সহায়ক',
        'Hello! I\'m your healthcare assistant. I can help you with symptoms, prevention tips, vaccination schedules, and emergency contacts. What would you like to know?': 'হ্যালো! আমি আপনার স্বাস্থ্য সহায়ক। আমি লক্ষণ, প্রতিরোধ টিপস, টিকাদান সময়সূচী এবং জরুরি যোগাযোগে আপনাকে সাহায্য করতে পারি। আপনি কী জানতে চান?',
        'Type your health question...': 'আপনার স্বাস্থ্য প্রশ্ন টাইপ করুন...',
        'Total Users': 'মোট ব্যবহারকারী',
        'Messages Processed': 'প্রক্রিয়াজাত বার্তা',
        'Supported Languages': 'সমর্থিত ভাষা',
        'Availability': 'উপলব্ধতা',
        'AI Healthcare Chatbot': 'AI স্বাস্থ্য চ্যাটবট',
        'Making healthcare information accessible to all.': 'সবার জন্য স্বাস্থ্য তথ্য সহজলভ্য করা।',
        'Built with': 'দিয়ে নির্মিত',
        'for rural healthcare': 'গ্রামীণ স্বাস্থ্যসেবার জন্য',
        'Send "Hello" to get started': 'শুরু করতে "Hello" পাঠান',
        'Text your health questions': 'আপনার স্বাস্থ্য প্রশ্ন পাঠান'
    },
    'te': {  # Telugu
        'AI-Powered Healthcare Assistant': 'AI-నడిచే ఆరోగ్య సహాయకుడు',
        'Features': 'లక్షణాలు',
        'Test Bot': 'బాట్ పరీక్షించండి',
        'Dashboard': 'డ్యాష్‌బోర్డ్',
        'Accessible healthcare information in your local language through WhatsApp and SMS. Get instant guidance on symptoms, prevention, and vaccination schedules.': 'WhatsApp మరియు SMS ద్వారా మీ స్థానిక భాషలో అందుబాటులో ఉన్న ఆరోగ్య సమాచారం. లక్షణాలు, నివారణ మరియు టీకా షెడ్యూల్‌ల గురించి తక్షణ మార్గదర్శకత్వం పొందండి.',
        'Key Features': 'ప్రధాన లక్షణాలు',
        'Comprehensive healthcare assistance at your fingertips': 'మీ వేళ్ల చివరలో సమగ్ర ఆరోగ్య సహాయం',
        'Multilingual Support': 'బహుభాషా మద్దతు',
        'Available in Hindi, English, Bengali, Telugu, Tamil, and other regional languages': 'హిందీ, ఆంగ్లం, బెంగాలీ, తెలుగు, తమిళం మరియు ఇతర ప్రాంతీయ భాషలలో అందుబాటులో ఉంది',
        'Symptom Analysis': 'లక్షణ విశ్లేషణ',
        'Intelligent symptom recognition and disease information with prevention tips': 'నివారణ చిట్కాలతో తెలివైన లక్షణ గుర్తింపు మరియు వ్యాధి సమాచారం',
        'Vaccination Reminders': 'టీకా గుర్తుచేతనలు',
        'Personalized vaccination schedules and automated reminders for all age groups': 'అన్ని వయస్సు సమూహాలకు వ్యక్తిగత టీకా షెడ్యూల్‌లు మరియు స్వయంచాలక గుర్తుచేతనలు',
        'Prevention Tips': 'నివారణ చిట్కాలు',
        'Evidence-based preventive health guidance for nutrition, exercise, and hygiene': 'పోషకాహారం, వ్యాయామం మరియు పరిశుభ్రత కోసం ఆధారిత నివారక ఆరోగ్య మార్గదర్శకత్వం',
        'Emergency Contacts': 'అత్యవసర సంప్రదింపులు',
        'Quick access to emergency numbers and health helplines': 'అత్యవసర నంబర్లు మరియు ఆరోగ్య హెల్ప్‌లైన్‌లకు వేగమైన ప్రవేశం',
        'Outbreak Alerts': 'వ్యాప్తి హెచ్చరికలు',
        'Real-time disease outbreak notifications and health advisories': 'రియల్-టైమ్ వ్యాధి వ్యాప్తి నోటిఫికేషన్‌లు మరియు ఆరోగ్య సలహాలు',
        'Test the Chatbot': 'చాట్‌బాట్‌ను పరీక్షించండి',
        'Try asking health-related questions below': 'క్రింద ఆరోగ్య-సంబంధిత ప్రశ్నలు అడగడానికి ప్రయత్నించండి',
        'Healthcare Assistant': 'ఆరోగ్య సహాయకుడు',
        'Hello! I\'m your healthcare assistant. I can help you with symptoms, prevention tips, vaccination schedules, and emergency contacts. What would you like to know?': 'హలో! నేను మీ ఆరోగ్య సహాయకుడిని. లక్షణాలు, నివారణ చిట్కాలు, టీకా షెడ్యూల్‌లు మరియు అత్యవసర సంప్రదింపులలో నేను మీకు సహాయపడగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?',
        'Type your health question...': 'మీ ఆరోగ్య ప్రశ్నను టైప్ చేయండి...',
        'Total Users': 'మొత్తం వినియోగదారులు',
        'Messages Processed': 'ప్రాసెస్ చేయబడిన సందేశాలు',
        'Supported Languages': 'సమర్థించిన భాషలు',
        'Availability': 'అందుబాటు',
        'AI Healthcare Chatbot': 'AI ఆరోగ్య చాట్‌బాట్',
        'Making healthcare information accessible to all.': 'అందరికీ ఆరోగ్య సమాచారాన్ని అందుబాటులోకి తెస్తోంది.',
        'Built with': 'తో నిర్మించబడింది',
        'for rural healthcare': 'గ్రామీణ ఆరోగ్య సంరక్షణ కోసం',
        'Send "Hello" to get started': 'ప్రారంభించడానికి "Hello" పంపండి',
        'Text your health questions': 'మీ ఆరోగ్య ప్రశ్నలను టెక్స్ట్ చేయండి'
    },
    'ta': {  # Tamil
        'AI-Powered Healthcare Assistant': 'AI-இயக்கப்படும் சுகாதார உதவியாளர்',
        'Features': 'அம்சங்கள்',
        'Test Bot': 'பாட் சோதிக்கவும்',
        'Dashboard': 'டாஷ்போர்டு',
        'Accessible healthcare information in your local language through WhatsApp and SMS. Get instant guidance on symptoms, prevention, and vaccination schedules.': 'WhatsApp மற்றும் SMS மூலம் உங்கள் உள்ளூர் மொழியில் அணுகக்கூடிய சுகாதார தகவல். அறிகுறிகள், தடுப்பு மற்றும் தடுப்பூசி அட்டவணைகள் பற்றி உடனடி வழிகாட்டுதல் பெறவும்.',
        'Key Features': 'முக்கிய அம்சங்கள்',
        'Comprehensive healthcare assistance at your fingertips': 'உங்கள் விரல்களின் நுனியில் விரிவான சுகாதார உதவி',
        'Multilingual Support': 'பல மொழி ஆதரவு',
        'Available in Hindi, English, Bengali, Telugu, Tamil, and other regional languages': 'இந்தி, ஆங்கிலம், வங்காளி, தெலுங்கு, தமிழ் மற்றும் பிற பிராந்திய மொழிகளில் கிடைக்கிறது',
        'Symptom Analysis': 'அறிகுறி பகுப்பாய்வு',
        'Intelligent symptom recognition and disease information with prevention tips': 'தடுப்பு குறிப்புகளுடன் அறிவார்ந்த அறிகுறி அங்கீகாரம் மற்றும் நோய் தகவல்',
        'Vaccination Reminders': 'தடுப்பூசி நினைவூட்டல்கள்',
        'Personalized vaccination schedules and automated reminders for all age groups': 'அனைத்து வயது குழுக்களுக்கும் தனிப்பயனாக்கப்பட்ட தடுப்பூசி அட்டவணைகள் மற்றும் தானியங்கி நினைவூட்டல்கள்',
        'Prevention Tips': 'தடுப்பு குறிப்புகள்',
        'Evidence-based preventive health guidance for nutrition, exercise, and hygiene': 'ஊட்டச்சத்து, உடற்பயிற்சி மற்றும் சுகாதாரத்திற்கான ஆதார அடிப்படையிலான தடுப்பு சுகாதார வழிகாட்டுதல்',
        'Emergency Contacts': 'அவசரகால தொடர்புகள்',
        'Quick access to emergency numbers and health helplines': 'அவசரகால எண்கள் மற்றும் சுகாதார உதவி வரிகளுக்கு விரைவான அணுகல்',
        'Outbreak Alerts': 'வெடிப்பு எச்சரிக்கைகள்',
        'Real-time disease outbreak notifications and health advisories': 'நேரடி நேர நோய் வெடிப்பு அறிவிப்புகள் மற்றும் சுகாதார ஆலோசனைகள்',
        'Test the Chatbot': 'சாட்பாடை சோதிக்கவும்',
        'Try asking health-related questions below': 'கீழே சுகாதார தொடர்பான கேள்விகளைக் கேட்க முயற்சிக்கவும்',
        'Healthcare Assistant': 'சுகாதார உதவியாளர்',
        'Hello! I\'m your healthcare assistant. I can help you with symptoms, prevention tips, vaccination schedules, and emergency contacts. What would you like to know?': 'வணக்கம்! நான் உங்கள் சுகாதார உதவியாளர். அறிகுறிகள், தடுப்பு குறிப்புகள், தடுப்பூசி அட்டவணைகள் மற்றும் அவசரகால தொடர்புகளில் உங்களுக்கு உதவ முடியும். நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?',
        'Type your health question...': 'உங்கள் சுகாதார கேள்வியை தட்டச்சு செய்யவும்...',
        'Total Users': 'மொத்த பயனர்கள்',
        'Messages Processed': 'செயலாக்கப்பட்ட செய்திகள்',
        'Supported Languages': 'ஆதரிக்கப்படும் மொழிகள்',
        'Availability': 'கிடைக்கும் தன்மை',
        'AI Healthcare Chatbot': 'AI சுகாதார சாட்பாட்',
        'Making healthcare information accessible to all.': 'அனைவருக்கும் சுகாதார தகவலை அணுகக்கூடியதாக மாற்றுகிறது.',
        'Built with': 'உடன் கட்டப்பட்டது',
        'for rural healthcare': 'கிராமப்புற சுகாதாரத்திற்காக',
        'Send "Hello" to get started': 'தொடங்க "Hello" அனுப்பவும்',
        'Text your health questions': 'உங்கள் சுகாதார கேள்விகளை அனுப்பவும்'
    }
}

def get_or_create_user(phone_number: str) -> User:
    """Get existing user or create a new one."""
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        user = User(phone_number=phone_number)
        db.session.add(user)
        db.session.commit()
    return user

def update_statistics(message_type: str, query_content: str):
    """Update daily statistics."""
    today = date.today()
    stats = HealthStatistics.query.filter_by(date=today).first()
    
    if not stats:
        stats = HealthStatistics(date=today)
        db.session.add(stats)
    
    # Update counters
    stats.total_messages += 1
    
    if message_type == 'whatsapp':
        stats.whatsapp_messages += 1
    elif message_type == 'sms':
        stats.sms_messages += 1
    
    # Categorize query type
    query_lower = query_content.lower()
    if any(word in query_lower for word in ['symptom', 'fever', 'headache', 'cough', 'pain']):
        stats.symptom_queries += 1
    elif any(word in query_lower for word in ['vaccine', 'vaccination', 'immunization']):
        stats.vaccination_queries += 1
    elif any(word in query_lower for word in ['prevent', 'prevention', 'healthy', 'tips']):
        stats.prevention_queries += 1
    elif any(word in query_lower for word in ['emergency', 'urgent', 'help']):
        stats.emergency_queries += 1
    
    # Update unique users count
    stats.unique_users = User.query.filter(
        User.created_at >= datetime.combine(today, datetime.min.time())
    ).count()
    
    db.session.commit()

@app.route('/')
def home():
    """Home page with project information."""
    current_locale = get_locale()
    
    # Set up translation context manually
    with app.app_context():
        # Create a simple gettext function that works with our setup
        def _(text):
            if current_locale in translations and text in translations[current_locale]:
                return translations[current_locale][text]
            return text
        
        return render_template('index.html', 
                             get_locale=lambda: current_locale,
                             gettext=_,
                             config=Config)

@app.route('/set_language/<language>')
def set_language(language=None):
    """Set the language for the current session."""
    if language in Config.SUPPORTED_LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('home'))

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages."""
    try:
        # Get message details
        from_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '')
        
        logger.info(f"Received WhatsApp message from {from_number}: {message_body}")
        
        if not from_number or not message_body:
            return 'Invalid request', 400
        
        # Get or create user
        user = get_or_create_user(from_number)
        
        # Detect language
        detected_lang = health_bot.detect_language(message_body)
        
        # Get response from chatbot
        raw_response = health_bot.get_contextual_response(
            message_body, 
            {'language': user.language or detected_lang}
        )
        
        # For WhatsApp, we'll use the raw response as HTML isn't supported well
        # But we'll clean it up a bit for better readability
        response = raw_response.replace('• ', '\n• ')
        response = response.replace('─────', '\n\n')
        
        # Save message to database
        message_record = Message(
            user_id=user.id,
            message_type='whatsapp',
            incoming_message=message_body,
            outgoing_message=response,
            detected_language=detected_lang
        )
        db.session.add(message_record)
        
        # Update user's preferred language if detected
        if not user.language and detected_lang != 'en':
            user.language = detected_lang
        
        db.session.commit()
        
        # Update statistics
        update_statistics('whatsapp', message_body)
        
        # Send response via Twilio
        twiml_response = MessagingResponse()
        twiml_response.message(response)
        
        return str(twiml_response)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")
        error_response = MessagingResponse()
        error_response.message(
            "Sorry, I'm experiencing technical difficulties. Please try again later or contact emergency services if this is urgent."
        )
        return str(error_response)

@app.route('/webhook/sms', methods=['POST'])
def sms_webhook():
    """Handle incoming SMS messages."""
    try:
        # Get message details
        from_number = request.form.get('From', '')
        message_body = request.form.get('Body', '')
        
        logger.info(f"Received SMS from {from_number}: {message_body}")
        
        if not from_number or not message_body:
            return 'Invalid request', 400
        
        # Get or create user
        user = get_or_create_user(from_number)
        
        # Detect language
        detected_lang = health_bot.detect_language(message_body)
        
        # Get response from chatbot
        raw_response = health_bot.get_contextual_response(
            message_body, 
            {'language': user.language or detected_lang}
        )
        
        # For SMS, use a simplified format for better readability
        response = raw_response.replace('• ', '\n• ')
        response = response.replace('─────', '\n\n')
        
        # Save message to database
        message_record = Message(
            user_id=user.id,
            message_type='sms',
            incoming_message=message_body,
            outgoing_message=response,
            detected_language=detected_lang
        )
        db.session.add(message_record)
        
        # Update user's preferred language
        if not user.language and detected_lang != 'en':
            user.language = detected_lang
        
        db.session.commit()
        
        # Update statistics
        update_statistics('sms', message_body)
        
        # Send response via Twilio
        twiml_response = MessagingResponse()
        twiml_response.message(response)
        
        return str(twiml_response)
        
    except Exception as e:
        logger.error(f"Error processing SMS: {str(e)}")
        error_response = MessagingResponse()
        error_response.message(
            "Sorry, I'm experiencing technical difficulties. Please try again later."
        )
        return str(error_response)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """API endpoint to send messages programmatically."""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')
        message_type = data.get('type', 'sms')  # 'sms' or 'whatsapp'
        
        if not phone_number or not message:
            return jsonify({'error': 'Phone number and message are required'}), 400
        
        if not twilio_client:
            return jsonify({'error': 'Twilio not configured'}), 500
        
        # Format phone number for Twilio
        if message_type == 'whatsapp':
            to_number = f'whatsapp:{phone_number}'
            from_number = Config.TWILIO_WHATSAPP_NUMBER
        else:
            to_number = phone_number
            from_number = Config.TWILIO_PHONE_NUMBER
        
        # Send message
        twilio_message = twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        return jsonify({
            'success': True,
            'message_sid': twilio_message.sid,
            'status': twilio_message.status
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages."""
    try:
        messages = Message.query.order_by(Message.created_at.desc()).limit(100).all()
        return jsonify([message.to_dict() for message in messages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get health statistics."""
    try:
        # Get today's statistics
        today_stats = HealthStatistics.query.filter_by(date=date.today()).first()
        
        # Get total statistics
        total_users = User.query.count()
        total_messages = Message.query.count()
        
        return jsonify({
            'today': today_stats.to_dict() if today_stats else None,
            'totals': {
                'total_users': total_users,
                'total_messages': total_messages
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/outbreak-alerts', methods=['GET', 'POST'])
def handle_outbreak_alerts():
    """Handle outbreak alerts."""
    try:
        if request.method == 'GET':
            alerts = OutbreakAlert.query.filter_by(is_active=True).all()
            return jsonify([alert.to_dict() for alert in alerts])
        
        elif request.method == 'POST':
            data = request.get_json()
            
            alert = OutbreakAlert(
                disease_name=data.get('disease_name'),
                alert_message=data.get('alert_message'),
                severity_level=data.get('severity_level', 'medium'),
                created_by=data.get('created_by', 'System')
            )
            
            if data.get('affected_locations'):
                alert.set_affected_locations(data['affected_locations'])
            
            db.session.add(alert)
            db.session.commit()
            
            return jsonify(alert.to_dict()), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Admin dashboard."""
    current_locale = get_locale()
    
    # Set up translation context manually
    with app.app_context():
        # Create a simple gettext function that works with our setup
        def _(text):
            if current_locale in translations and text in translations[current_locale]:
                return translations[current_locale][text]
            return text
        
        return render_template('dashboard.html',
                             get_locale=lambda: current_locale,
                             gettext=_,
                             config=Config)

@app.route('/api/test-chatbot', methods=['POST'])
def test_chatbot():
    """Test the chatbot functionality."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'en')
        response_format = data.get('format', 'html')  # Default to HTML formatted response
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get raw response from chatbot
        raw_response = health_bot.get_contextual_response(
            message, 
            {'language': language}
        )
        
        # Format response for display
        if response_format == 'html':
            formatted_response = ResponseFormatter.format_for_html(raw_response)
        else:
            formatted_response = raw_response
        
        return jsonify({
            'message': message,
            'response': {
                'raw': raw_response,
                'formatted': formatted_response
            },
            'detected_language': health_bot.detect_language(message)
        })
        
    except Exception as e:
        logger.error(f"Error testing chatbot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image-diagnosis', methods=['POST'])
def image_diagnosis():
    """
    Accepts an image and language, returns a mock AI diagnosis.
    Does not store the image. Ready for real model integration.
    Now uses filename and brightness for more realistic feedback.
    """
    if 'image' not in request.files:
        return jsonify({'feedback': 'No image uploaded.'}), 400
    image = request.files['image']
    language = request.form.get('language', 'en')
    image_bytes = image.read()  # Do not store the image
    filename = image.filename or ''
    feedback = mock_image_classifier(image_bytes, language=language, filename=filename)
    return jsonify({'feedback': feedback})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', Config.PORT))
    debug = Config.DEBUG
    
    print(f"Starting Healthcare Chatbot on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
