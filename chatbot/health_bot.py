import json
import re
import os
from typing import Dict, List, Tuple, Optional
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class HealthChatbot:
    def __init__(self):
        self.translator = GoogleTranslator(source="auto", target="en")  
        self.knowledge_base = self._load_knowledge_base()
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.symptom_vectors = None
        self.disease_names = []
        self._prepare_symptom_matching()
        
    def _load_knowledge_base(self) -> Dict:
        """Load the health knowledge base from JSON file."""
        try:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_path, 'data', 'health_knowledge_base.json')
            with open(kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "diseases": {},
                "preventive_health": {},
                "vaccination_schedules": {},
                "emergency_contacts": {}
            }
    
    def _prepare_symptom_matching(self):
        """Prepare symptom vectors for similarity matching."""
        all_symptoms = []
        self.disease_names = []
        
        for disease, info in self.knowledge_base.get('diseases', {}).items():
            symptoms = ' '.join(info.get('symptoms', []))
            all_symptoms.append(symptoms)
            self.disease_names.append(disease)
        
        if all_symptoms:
            self.symptom_vectors = self.vectorizer.fit_transform(all_symptoms)
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text."""
        try:
            lang = detect(text)
            return lang if lang in ['hi', 'bn', 'te', 'ta', 'gu', 'kn', 'ml', 'pa', 'mr'] else 'en'
        except LangDetectException:
            return 'en'
    
    def translate_text(self, text: str, target_lang: str = 'en', source_lang: str = 'auto') -> str:
        """Translate text between languages."""
        try:
            if source_lang == target_lang:
                return text
            return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess the input text."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract potential symptoms from user input."""
        text = self.preprocess_text(text)
        tokens = word_tokenize(text)
        
        # Common symptom keywords
        symptom_keywords = [
            'fever', 'headache', 'cough', 'cold', 'pain', 'ache', 'nausea',
            'vomiting', 'diarrhea', 'weakness', 'fatigue', 'dizziness',
            'breathing', 'chest', 'stomach', 'throat', 'runny', 'nose',
            'chills', 'sweating', 'temperature', 'thirst', 'urination',
            'weight', 'loss', 'blurred', 'vision', 'muscle', 'cramps'
        ]
        
        found_symptoms = []
        for token in tokens:
            if token in symptom_keywords:
                found_symptoms.append(token)
        
        return found_symptoms
    
    def match_symptoms_to_disease(self, symptoms: List[str]) -> List[Tuple[str, float]]:
        """Match symptoms to diseases using similarity scoring."""
        if not symptoms or self.symptom_vectors is None:
            return []
        
        user_symptoms = ' '.join(symptoms)
        user_vector = self.vectorizer.transform([user_symptoms])
        
        similarities = cosine_similarity(user_vector, self.symptom_vectors)[0]
        
        # Get top 3 matches
        top_indices = np.argsort(similarities)[::-1][:3]
        matches = []
        
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                disease = self.disease_names[idx]
                matches.append((disease, similarities[idx]))
        
        return matches
    
    def get_disease_info(self, disease: str) -> Dict:
        """Get comprehensive information about a specific disease."""
        return self.knowledge_base.get('diseases', {}).get(disease, {})
    
    def get_preventive_health_info(self, category: str = None) -> Dict:
        """Get preventive health information."""
        preventive = self.knowledge_base.get('preventive_health', {})
        if category:
            return preventive.get(category, {})
        return preventive
    
    def get_vaccination_schedule(self, age_group: str = 'children') -> Dict:
        """Get vaccination schedule for specified age group."""
        schedules = self.knowledge_base.get('vaccination_schedules', {})
        return schedules.get(age_group, {})
    
    def get_emergency_contacts(self) -> Dict:
        """Get emergency contact numbers."""
        return self.knowledge_base.get('emergency_contacts', {})
    
    def process_query(self, message: str, user_language: str = None) -> str:
        """Process user query and return appropriate response."""
        # Detect language if not provided
        if not user_language:
            user_language = self.detect_language(message)
        
        # Translate to English for processing
        english_message = self.translate_text(message, 'en', user_language)
        english_message_lower = english_message.lower()
        
        response = ""
        
        # Check for greetings
        if any(word in english_message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
            # Get translated greeting based on language
            greeting_responses = {
                'hi': "नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। मैं आपकी मदद कर सकता हूं:\n"
                      "• रोग के लक्षण और जानकारी\n"
                      "• निवारक स्वास्थ्य सुझाव\n"
                      "• टीकाकरण कार्यक्रम\n"
                      "• आपातकालीन संपर्क\n"
                      "• स्वास्थ्य सलाह और मार्गदर्शन\n\n"
                      "आप क्या जानना चाहते हैं?",
                'bn': "হ্যালো! আমি আপনার স্বাস্থ্য সহায়ক। আমি আপনাকে সাহায্য করতে পারি:\n"
                      "• রোগের লক্ষণ এবং তথ্য\n"
                      "• প্রতিরোধমূলক স্বাস্থ্য টিপস\n"
                      "• টিকাদান সময়সূচী\n"
                      "• জরুরি যোগাযোগ\n"
                      "• স্বাস্থ্য পরামর্শ এবং নির্দেশনা\n\n"
                      "আপনি কী জানতে চান?",
                'te': "హలో! నేను మీ ఆరోగ్య సహాయకుడిని. నేను మీకు సహాయపడగలను:\n"
                      "• వ్యాధి లక్షణాలు మరియు సమాచారం\n"
                      "• నివారక ఆరోగ్య చిట్కాలు\n"
                      "• టీకా షెడ్యూల్‌లు\n"
                      "• అత్యవసర సంప్రదింపులు\n"
                      "• ఆరోగ్య సలహాలు మరియు మార్గదర్శకత్వం\n\n"
                      "మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?",
                'ta': "வணக்கம்! நான் உங்கள் சுகாதார உதவியாளர். நான் உங்களுக்கு உதவ முடியும்:\n"
                      "• நோயின் அறிகுறிகள் மற்றும் தகவல்\n"
                      "• தடுப்பு சுகாதார குறிப்புகள்\n"
                      "• தடுப்பூசி அட்டவணைகள்\n"
                      "• அவசரகால தொடர்புகள்\n"
                      "• சுகாதார ஆலோசனைகள் மற்றும் வழிகாட்டுதல்\n\n"
                      "நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?"
            }
            
            if user_language in greeting_responses:
                response = greeting_responses[user_language]
            else:
                response = "Hello! I'm your health assistant. I can help you with:\n"
                response += "• Disease symptoms and information\n"
                response += "• Preventive health tips\n"
                response += "• Vaccination schedules\n"
                response += "• Emergency contacts\n"
                response += "• Health advice and guidance\n\n"
                response += "What would you like to know about?"
        
        # Check for emergency keywords
        elif any(word in english_message_lower for word in ['emergency', 'urgent', 'ambulance', 'help']):
            contacts = self.get_emergency_contacts()
            
            # Get translated emergency response based on language
            emergency_responses = {
                'hi': "🚨 आपातकालीन संपर्क 🚨\n\n"
                      "राष्ट्रीय हेल्पलाइन:\n"
                      "• एम्बुलेंस: 108\n"
                      "• पुलिस: 100\n"
                      "• फायर: 101\n\n"
                      "यदि यह चिकित्सा आपातकाल है, तो तुरंत 108 पर कॉल करें!",
                'bn': "🚨 জরুরি যোগাযোগ 🚨\n\n"
                      "জাতীয় হেল্পলাইন:\n"
                      "• অ্যাম্বুলেন্স: ১০৮\n"
                      "• পুলিশ: ১০০\n"
                      "• ফায়ার: ১০১\n\n"
                      "যদি এটি একটি চিকিৎসা জরুরি, তাহলে অবিলম্বে ১০৮ এ কল করুন!",
                'te': "🚨 అత్యవసర సంప్రదింపులు 🚨\n\n"
                      "జాతీయ హెల్ప్‌లైన్‌లు:\n"
                      "• అంబులెన్స్: 108\n"
                      "• పోలీసు: 100\n"
                      "• అగ్నిమాపక: 101\n\n"
                      "ఇది వైద్య అత్యవసర సమయమైతే, వెంటనే 108 కి కాల్ చేయండి!",
                'ta': "🚨 அவசரகால தொடர்புகள் 🚨\n\n"
                      "தேசிய உதவி வரிகள்:\n"
                      "• ஆம்புலன்ஸ்: 108\n"
                      "• காவல்துறை: 100\n"
                      "• தீயணைப்பு: 101\n\n"
                      "இது மருத்துவ அவசரகாலமாக இருந்தால், உடனடியாக 108 க்கு அழைக்கவும்!"
            }
            
            if user_language in emergency_responses:
                response = emergency_responses[user_language]
            else:
                response = "🚨 EMERGENCY CONTACTS 🚨\n\n"
                if 'national_helplines' in contacts:
                    response += "National Helplines:\n"
                    for service, number in contacts['national_helplines'].items():
                        response += f"• {service.title()}: {number}\n"
                response += "\nIf this is a medical emergency, call 108 immediately!"
        
        # Check for vaccination queries
        elif any(word in english_message_lower for word in ['vaccine', 'vaccination', 'immunization']):
            if 'child' in english_message_lower or 'baby' in english_message_lower:
                schedule = self.get_vaccination_schedule('children')
                response = "👶 CHILD VACCINATION SCHEDULE:\n\n"
                for age, vaccines in schedule.items():
                    response += f"At {age.replace('_', ' ')}: {', '.join(vaccines)}\n"
            else:
                schedule = self.get_vaccination_schedule('adults')
                response = "👨 ADULT VACCINATION SCHEDULE:\n\n"
                for frequency, vaccines in schedule.items():
                    if frequency != 'special_groups':
                        response += f"{frequency.title()}: {', '.join(vaccines)}\n"
        
        # Check for preventive health queries
        elif any(word in english_message_lower for word in ['prevent', 'prevention', 'healthy', 'tips', 'diet', 'exercise']):
            preventive = self.get_preventive_health_info()
            response = "🏥 PREVENTIVE HEALTH TIPS:\n\n"
            
            if 'exercise' in english_message_lower:
                response += "💪 EXERCISE RECOMMENDATIONS:\n"
                for tip in preventive.get('exercise', {}).get('recommendations', []):
                    response += f"• {tip}\n"
            elif 'diet' in english_message_lower or 'nutrition' in english_message_lower:
                response += "🥗 NUTRITION GUIDELINES:\n"
                for tip in preventive.get('nutrition', {}).get('guidelines', []):
                    response += f"• {tip}\n"
            else:
                # General preventive tips
                for category, info in preventive.items():
                    response += f"\n{category.replace('_', ' ').title()}:\n"
                    for key, tips in info.items():
                        for tip in tips:
                            response += f"• {tip}\n"
        
        # Check for symptom-based queries
        else:
            symptoms = self.extract_symptoms(english_message)
            if symptoms:
                matches = self.match_symptoms_to_disease(symptoms)
                if matches:
                    response = "📋 Based on your symptoms, here's what I found:\n\n"
                    
                    for disease, confidence in matches:
                        disease_info = self.get_disease_info(disease)
                        # Create a visually distinct header for each disease
                        response += f"━━━━━━━━━━ 🔍 {disease.replace('_', ' ').upper()} ━━━━━━━━━━\n"
                        response += f"{disease_info.get('description', '')}\n\n"
                        
                        if 'symptoms' in disease_info:
                            response += "🤒 SYMPTOMS\n"
                            symptoms_list = disease_info['symptoms']
                            # Format symptoms in bullet points for better readability
                            response += "• " + "\n• ".join(symptoms_list) + "\n\n"
                        
                        if 'prevention' in disease_info:
                            response += "🛡️ PREVENTION\n"
                            for prev in disease_info['prevention']:
                                response += f"• {prev}\n"
                            response += "\n"
                        
                        if 'when_to_seek_help' in disease_info:
                            response += "⚠️ SEEK MEDICAL HELP IF:\n"
                            for warning in disease_info['when_to_seek_help']:
                                response += f"• {warning}\n"
                        
                        # Add extra spacing between diseases
                        response += "\n\n"
                else:
                    response = "I understand you're experiencing some symptoms. While I can provide general health information, it's important to consult with a healthcare professional for proper diagnosis and treatment.\n\n"
                    response += "For immediate medical concerns, please contact:\n"
                    response += "• Emergency: 108\n"
                    response += "• Medical Emergency: 102"
            else:
                # General health response
                response = "I'm here to help with health information! You can ask me about:\n\n"
                response += "• Symptoms (e.g., 'I have fever and headache')\n"
                response += "• Disease prevention\n"
                response += "• Vaccination schedules\n"
                response += "• Emergency contacts\n"
                response += "• General health tips\n\n"
                response += "What would you like to know?"
        
        # Add disclaimer
        response += "\n\n⚠️ Disclaimer: This information is for educational purposes only. Please consult a healthcare professional for medical advice."
        
        # Translate response back to user's language if needed
        if user_language != 'en':
            response = self.translate_text(response, user_language, 'en')
        
        return response
    
    def get_contextual_response(self, message: str, user_data: Dict = None) -> str:
        """Get contextual response based on user data and history."""
        user_language = user_data.get('language', 'en') if user_data else 'en'
        return self.process_query(message, user_language)