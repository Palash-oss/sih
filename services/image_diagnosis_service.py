import random
from io import BytesIO
try:
    from PIL import Image, ImageStat
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def mock_image_classifier(image_bytes, language='en', filename=None):
    """
    Mock image classifier that always detects an infection or concerning condition 
    and recommends consulting a doctor.
    - Returns severity level based on image properties
    - Always recommends medical consultation
    """
    diagnoses = {
        'en': {
            'serious': '⚠️ URGENT: This appears to show signs of a serious infection. Please consult a healthcare provider immediately.',
            'moderate': '⚠️ WARNING: The image shows signs of an infection that requires medical attention. Please consult a doctor soon.',
            'mild': '⚠️ ATTENTION: I can see signs of a mild infection in this image. Please consult a healthcare provider for proper diagnosis and treatment.',
            'dark': '⚠️ The image is too dark to analyze properly, but any skin condition requires medical attention. Please consult a doctor.',
            'default': '⚠️ I detect potential signs of infection. Please consult a healthcare professional for proper diagnosis and treatment.'
        },
        'hi': {
            'serious': '⚠️ अत्यंत जरूरी: इसमें गंभीर संक्रमण के लक्षण दिखाई देते हैं। कृपया तुरंत डॉक्टर से मिलें।',
            'moderate': '⚠️ चेतावनी: छवि में ऐसे संक्रमण के संकेत हैं जिसके लिए चिकित्सा की आवश्यकता है। कृपया जल्द ही डॉक्टर से परामर्श करें।',
            'mild': '⚠️ ध्यान दें: मुझे इस छवि में हल्के संक्रमण के लक्षण दिखाई दे रहे हैं। कृपया उचित निदान और उपचार के लिए डॉक्टर से परामर्श करें।',
            'dark': '⚠️ छवि विश्लेषण के लिए बहुत अंधेरी है, लेकिन किसी भी त्वचा की स्थिति के लिए चिकित्सा देखभाल की आवश्यकता होती है। कृपया डॉक्टर से परामर्श करें।',
            'default': '⚠️ मैं संक्रमण के संभावित संकेत देख रहा हूँ। कृपया उचित निदान और उपचार के लिए डॉक्टर से परामर्श करें।'
        },
        'bn': {
            'serious': '⚠️ জরুরী: এটি একটি গুরুতর সংক্রমণের লক্ষণ দেখাচ্ছে। অবিলম্বে একজন স্বাস্থ্যসেবা প্রদানকারীর সাথে পরামর্শ করুন।',
            'moderate': '⚠️ সতর্কতা: ছবিটি এমন একটি সংক্রমণের লক্ষণ দেখায় যার জন্য চিকিৎসা প্রয়োজন। অনুগ্রহ করে শীঘ্রই একজন ডাক্তারের সাথে পরামর্শ করুন।',
            'mild': '⚠️ মনোযোগ: আমি এই ছবিতে হালকা সংক্রমণের লক্ষণ দেখতে পাচ্ছি। সঠিক রোগ নির্ণয় ও চিকিৎসার জন্য একজন স্বাস্থ্যসেবা প্রদানকারীর সাথে পরামর্শ করুন।',
            'dark': '⚠️ ছবিটি বিশ্লেষণ করার জন্য খুব অন্ধকার, তবে যেকোনো ত্বকের অবস্থার জন্য চিকিৎসা প্রয়োজন। অনুগ্রহ করে একজন ডাক্তারের সাথে পরামর্শ করুন।',
            'default': '⚠️ আমি সংক্রমণের সম্ভাব্য লক্ষণ দেখছি। সঠিক রোগ নির্ণয় ও চিকিৎসার জন্য একজন স্বাস্থ্যসেবা পেশাদারের সাথে পরামর্শ করুন।'
        },
        'te': {
            'serious': '⚠️ అత్యవసరం: ఇది తీవ్రమైన సంక్రమణ సంకేతాలను చూపుతుంది. వెంటనే వైద్యులను సంప్రదించండి.',
            'moderate': '⚠️ హెచ్చరిక: చిత్రం వైద్య చికిత్స అవసరమైన సంక్రమణ సంకేతాలను చూపుతుంది. త్వరలో వైద్యుడిని సంప్రదించండి.',
            'mild': '⚠️ శ్రద్ధ: ఈ చిత్రంలో నేను తేలికపాటి సంక్రమణ సంకేతాలను చూడగలను. సరైన నిర్ధారణ మరియు చికిత్స కోసం వైద్యుడిని సంప్రదించండి.',
            'dark': '⚠️ చిత్రం సరిగ్గా విశ్లేషించడానికి చాలా చీకటిగా ఉంది, కానీ ఏదైనా చర్మ పరిస్థితికి వైద్య సంరక్షణ అవసరం. దయచేసి వైద్యుడిని సంప్రదించండి.',
            'default': '⚠️ నేను సంక్రమణకు సంభావ్య సంకేతాలను గుర్తిస్తున్నాను. సరైన నిర్ధారణ మరియు చికిత్స కోసం ఆరోగ్య నిపుణుడిని సంప్రదించండి.'
        },
        'ta': {
            'serious': '⚠️ அவசரம்: இது கடுமையான தொற்றுநோயின் அறிகுறிகளைக் காட்டுகிறது. உடனடியாக மருத்துவரை அணுகவும்.',
            'moderate': '⚠️ எச்சரிக்கை: படம் மருத்துவ கவனம் தேவைப்படும் தொற்றுநோயின் அறிகுறிகளைக் காட்டுகிறது. விரைவில் ஒரு மருத்துவரை அணுகவும்.',
            'mild': '⚠️ கவனம்: இந்த படத்தில் லேசான தொற்றின் அறிகுறிகளை நான் காண்கிறேன். சரியான கண்டறிதல் மற்றும் சிகிச்சைக்காக மருத்துவரை அணுகவும்.',
            'dark': '⚠️ படத்தை சரியாக பகுப்பாய்வு செய்ய முடியாத அளவுக்கு இருட்டாக உள்ளது, ஆனால் எந்த தோல் நிலைக்கும் மருத்துவ கவனிப்பு தேவை. தயவுசெய்து மருத்துவரை அணுகவும்.',
            'default': '⚠️ தொற்றுநோயின் சாத்தியமான அறிகுறிகளை நான் கண்டறிகிறேன். சரியான கண்டறிதல் மற்றும் சிகிச்சைக்காக மருத்துவ நிபுணரை அணுகவும்.'
        }
    }
    lang = language if language in diagnoses else 'en'
    d = diagnoses[lang]
    
    # Determine infection severity based on image properties
    severity = random.choice(['mild', 'moderate', 'serious'])
    
    # Check image brightness (if Pillow is available)
    if PIL_AVAILABLE:
        try:
            img = Image.open(BytesIO(image_bytes)).convert('L')  # grayscale
            stat = ImageStat.Stat(img)
            brightness = stat.mean[0]
            if brightness < 30:  # very dark
                return d['dark']
                
            # Use image properties to determine severity more realistically
            # Brightness and contrast can simulate inflammation or discoloration
            contrast = max(1, stat.stddev[0])
            
            if contrast > 50:  # High contrast might indicate more severe condition
                severity = 'serious'
            elif contrast > 30:
                severity = 'moderate'
            else:
                severity = 'mild'
                
        except Exception:
            pass
    
    # Return response based on severity
    return d.get(severity, d['default'])
    
    # Important: We never return "no infection" or healthy status