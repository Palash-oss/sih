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
    
    def format_disease_info(self, disease_name: str, disease_info: dict) -> str:
        """Format disease information with proper spacing and structure."""
        response = []
        
        # Add disease header
        response.append(f"\n🔍 {disease_name.upper()}")
        response.append(f"{disease_info.get('description', '')}\n")
        
        # Add symptoms section
        if 'symptoms' in disease_info:
            response.append("🤒 SYMPTOMS")
            for symptom in disease_info['symptoms']:
                response.append(f"• {symptom}")
            response.append("")  # Empty line for spacing
        
        # Add prevention section
        if 'prevention' in disease_info:
            response.append("🛡️ PREVENTION")
            for prev in disease_info['prevention']:
                response.append(f"• {prev}")
            response.append("")  # Empty line for spacing
        
        # Add warning signs
        if 'when_to_seek_help' in disease_info:
            response.append("⚠️ SEEK MEDICAL HELP IF:")
            for warning in disease_info['when_to_seek_help']:
                response.append(f"• {warning}")
            response.append("")  # Empty line for spacing
        
        return "\n".join(response)

    def format_response(self, matches):
        """Format the response with proper markdown and spacing"""
        sections = []
        
        # Header
        sections.append("📋 Based on your symptoms, here's what I found:\n")

        for disease, confidence in matches:
            # Disease Section with confidence score
            sections.append(f"🔍 {disease.replace('_', ' ').upper()}")
            info = self.get_disease_info(disease)
            sections.append(f"{info.get('description', '')}\n")

            # Symptoms Section
            if 'symptoms' in info:
                sections.append("🤒 SYMPTOMS")
                symptoms = info['symptoms']
                # Format symptoms in two columns
                for i in range(0, len(symptoms), 2):
                    if i + 1 < len(symptoms):
                        sections.append(f"• {symptoms[i]:<30} • {symptoms[i+1]}")
                    else:
                        sections.append(f"• {symptoms[i]}")
                sections.append("")

            # Prevention Section
            if 'prevention' in info:
                sections.append("🛡️ PREVENTION")
                for step in info['prevention']:
                    sections.append(f"• {step}")
                sections.append("")

            # Warning Signs Section
            if 'when_to_seek_help' in info:
                sections.append("⚠️ SEEK MEDICAL HELP IF:")
                for warning in info['when_to_seek_help']:
                    sections.append(f"• {warning}")
                sections.append("")

            # Separator between diseases
            sections.append("─" * 40 + "\n")

        # Disclaimer
        sections.append("⚠️ Disclaimer: This information is for educational purposes only. Please consult a healthcare professional for medical advice.")

        return "\n".join(sections)

    def get_contextual_response(self, message: str, context: dict = None) -> str:
        """Get a formatted response based on the user's message and context."""
        # Detect language if not provided in context
        user_language = context.get('language', self.detect_language(message))
        
        # Translate to English for processing if needed
        if user_language != 'en':
            message = self.translate_text(message, target_lang='en', source_lang=user_language)
        
        # Extract symptoms and get matches
        symptoms = self.extract_symptoms(message)
        if not symptoms:
            response = "I couldn't identify any symptoms. Could you please describe how you're feeling?"
        else:
            matches = self.match_symptoms_to_disease(symptoms)
            response = self.format_response(matches)
        
        # Translate response back if needed
        if user_language != 'en':
            response = self.translate_text(response, target_lang=user_language, source_lang='en')
        
        return response