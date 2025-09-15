# AI-Powered Multilingual Healthcare Chatbot

A comprehensive healthcare chatbot solution designed to provide accessible health information to rural and semi-urban communities through WhatsApp and SMS. Built with AI-powered multilingual support, symptom recognition, vaccination reminders, and outbreak alerts.

## 🌟 Features

- **Multilingual Support**: Hindi, English, Bengali, Telugu, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Marathi
- **WhatsApp & SMS Integration**: Accessible via Twilio API
- **Intelligent Symptom Recognition**: AI-powered disease symptom matching
- **Vaccination Reminders**: Automated personalized vaccination schedules
- **Preventive Health Information**: Nutrition, exercise, and hygiene guidance
- **Emergency Contacts**: Quick access to health helplines
- **Outbreak Alerts**: Real-time disease outbreak notifications
- **Admin Dashboard**: Comprehensive monitoring and management interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Twilio account (for WhatsApp and SMS)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sih
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env with your configuration
   ```

5. **Configure Twilio credentials** (Required)
   - Sign up at [Twilio](https://www.twilio.com)
   - Get your Account SID and Auth Token
   - Set up WhatsApp Sandbox
   - Update `.env` file with credentials

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Create environment file**
   ```bash
   cp .env.template .env
   # Edit .env with your Twilio credentials
   ```

2. **Run with Docker Compose**
   ```bash
   # Development
   docker-compose up --build
   
   # Production with Nginx
   docker-compose --profile production up --build -d
   ```

### Manual Docker Build

```bash
# Build the image
docker build -t healthcare-chatbot .

# Run the container
docker run -p 5000:5000 --env-file .env healthcare-chatbot
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Yes |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Yes |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number for SMS | Yes |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | Yes |
| `OPENAI_API_KEY` | OpenAI API key for enhanced responses | No |
| `GOOGLE_TRANSLATE_API_KEY` | Google Translate API key | No |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | Yes |
| `DATABASE_URL` | Database connection string | No |
| `ENABLE_VACCINATION_REMINDERS` | Enable vaccination reminders | No |

### Twilio Setup

1. **Create Twilio Account**: Sign up at [twilio.com](https://www.twilio.com)

2. **WhatsApp Sandbox Setup**:
   - Go to Console → Messaging → Try it out → Send a WhatsApp message
   - Follow instructions to join sandbox
   - Use sandbox number in your `.env` file

3. **SMS Setup**:
   - Purchase a phone number in Twilio Console
   - Add the number to your `.env` file

4. **Webhook Configuration**:
   ```
   WhatsApp Webhook URL: https://your-domain.com/webhook/whatsapp
   SMS Webhook URL: https://your-domain.com/webhook/sms
   ```

## 📱 Usage

### WhatsApp

1. Send "Hello" to the WhatsApp sandbox number
2. Ask health-related questions in any supported language
3. Examples:
   - "I have fever and headache"
   - "मुझे बुखार है" (Hindi)
   - "What vaccinations does my baby need?"

### SMS

1. Send a text message to your Twilio phone number
2. Ask health questions or request information
3. The bot will respond with relevant health guidance

### Web Interface

- **Homepage**: `http://localhost:5000` - Test the chatbot and view features
- **Admin Dashboard**: `http://localhost:5000/dashboard` - Monitor usage and manage alerts

## 🏗️ Project Structure

```
sih/
├── app.py                          # Main Flask application
├── config.py                       # Application configuration
├── models.py                       # Database models
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker container configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.template                   # Environment variables template
├── README.md                       # This file
├── chatbot/
│   └── health_bot.py              # Core chatbot logic
├── data/
│   └── health_knowledge_base.json # Health information database
├── services/
│   └── vaccination_reminder.py   # Vaccination reminder system
└── templates/
    ├── index.html                 # Homepage template
    └── dashboard.html             # Admin dashboard template
```

## 🔧 API Endpoints

### Public Endpoints

- `GET /` - Homepage
- `POST /webhook/whatsapp` - WhatsApp webhook
- `POST /webhook/sms` - SMS webhook
- `GET /dashboard` - Admin dashboard

### API Endpoints

- `GET /api/statistics` - Get usage statistics
- `GET /api/users` - Get all users
- `GET /api/messages` - Get recent messages
- `GET /api/outbreak-alerts` - Get active alerts
- `POST /api/outbreak-alerts` - Create new alert
- `POST /api/send-message` - Send message programmatically
- `POST /api/test-chatbot` - Test chatbot functionality

## 🌐 Deployment

### Production Deployment

1. **Server Setup**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy Application**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sih
   
   # Configure environment
   cp .env.template .env
   nano .env  # Add your configuration
   
   # Deploy with production profile
   docker-compose --profile production up -d --build
   ```

3. **SSL Configuration** (Optional):
   - Use Let's Encrypt with Certbot
   - Configure Nginx for HTTPS
   - Update webhook URLs to use HTTPS

### Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI and login
heroku create healthcare-chatbot-app

# Set environment variables
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
# ... add other variables

# Deploy
git push heroku main
```

#### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Configure environment variables in the platform
- Set up load balancer for high availability

## 🧪 Testing

### Manual Testing

1. **Test Chatbot**:
   - Visit `http://localhost:5000`
   - Use the test interface to ask health questions

2. **Test WhatsApp**:
   - Send messages to your Twilio WhatsApp sandbox
   - Try different languages and question types

3. **Test SMS**:
   - Send SMS to your Twilio phone number
   - Verify responses are received

### Automated Testing

```bash
# Run tests (if available)
python -m pytest tests/

# Test API endpoints
curl http://localhost:5000/api/statistics
```

## 🔒 Security

- **Environment Variables**: Never commit sensitive credentials
- **HTTPS**: Use SSL certificates in production
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Input Validation**: All user inputs are sanitized
- **Database Security**: Use environment variables for database credentials

## 📊 Monitoring

The admin dashboard provides:
- Real-time usage statistics
- User management
- Message monitoring
- Outbreak alert management
- Vaccination reminder tracking

Access at: `http://localhost:5000/dashboard`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

1. **Twilio Webhook Issues**:
   - Ensure your server is accessible from the internet
   - Use ngrok for local testing: `ngrok http 5000`
   - Check webhook URLs are correctly configured

2. **Database Issues**:
   - Database is created automatically on first run
   - Check file permissions in the application directory

3. **Translation Issues**:
   - Google Translate API key is optional
   - Basic translation works without API key

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Create a new issue with:
  - Error description
  - Steps to reproduce
  - Environment details
  - Log output

## 🏥 Healthcare Disclaimer

This chatbot provides general health information for educational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

## 📞 Emergency

For medical emergencies, always contact local emergency services:
- India: 108 (Ambulance)
- India: 102 (Medical Emergency)

---

**Built with ❤️ for accessible healthcare**#   S I H 2 5  
 #   s i h  
 