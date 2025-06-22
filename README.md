# AI Therapy Chatbot

An advanced AI-powered therapy chatbot that provides emotional support, practical coping strategies, and personalized therapeutic responses. The chatbot features emotion recognition, image analysis, voice interaction, and comprehensive remedy suggestions.

## Features

- **Emotion Recognition**: Real-time emotion detection from text input
- **Image Analysis**: Upload images to analyze emotional content using Gemini Pro Vision
- **Voice Interaction**: Text-to-speech for AI responses (voice input requires microphone)
- **Comprehensive Remedies**: Immediate, physical, cognitive, and mindfulness-based coping strategies
- **Database Storage**: PostgreSQL integration for conversation history and emotion tracking
- **Therapeutic AI**: Powered by Google's Gemini Pro for empathetic and solution-focused responses

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database (optional, app will work without it)
- Gemini API key from Google AI Studio

### Setup

1. **Clone or download the application files**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   ```

   **Getting a Gemini API Key:**
   - Go to [Google AI Studio](https://ai.google.dev)
   - Create a free account
   - Navigate to the API keys section
   - Create a new API key

4. **Install system dependencies (for voice features)**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   ```
   
   **On macOS:**
   ```bash
   brew install portaudio
   ```
   
   **On Windows:**
   - PyAudio may require Visual Studio Build Tools
   - Alternative: Use conda install pyaudio

5. **Set up PostgreSQL (optional)**
   
   If you want to use database features:
   - Install PostgreSQL
   - Create a database
   - Update the DATABASE_URL in your .env file

## Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8501`
   - The app will automatically create database tables if connected

## Usage

### Text Conversations
- Type messages in the chat input
- Get immediate emotional analysis and therapeutic responses
- Receive practical coping strategies for detected emotions

### Quick Help Buttons
- Use preset buttons for common issues (anxiety, sadness, anger)
- Get instant access to relevant therapeutic techniques

### Image Analysis
- Upload photos, artwork, or any images
- Get emotional analysis of visual content
- Receive therapy suggestions based on image content
- Face detection provides additional emotional insights

### Voice Features
- Text-to-speech for all AI responses
- Voice input (if microphone is available)
- Audio feedback for better accessibility

### Emotion Tracking
- View real-time emotion indicators
- Track emotional patterns over time
- Visual charts showing emotion distribution

## File Structure

```
ai-therapy-chatbot/
├── app.py                 # Main Streamlit application
├── emotion_detector.py    # Multi-method emotion detection
├── therapeutic_ai.py      # Gemini-powered therapeutic responses
├── image_analyzer.py      # Image emotion analysis with Gemini Vision
├── remedy_generator.py    # Comprehensive coping strategies
├── voice_handler.py       # Speech-to-text and text-to-speech
├── session_manager.py     # Session and conversation management
├── database.py           # PostgreSQL database integration
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .streamlit/
    └── config.toml      # Streamlit configuration
```

## Configuration

### Streamlit Configuration (`.streamlit/config.toml`)
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Environment Variables
- `GEMINI_API_KEY`: Required for AI responses and image analysis
- `DATABASE_URL`: Optional PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`: PostgreSQL connection details

## Troubleshooting

### Common Issues

1. **Voice features not working**
   - Install system audio dependencies
   - Check microphone permissions
   - Voice input disabled in environments without audio hardware

2. **Database connection errors**
   - App works without database (uses in-memory storage)
   - Check PostgreSQL connection details
   - Ensure database exists and is accessible

3. **API key errors**
   - Verify Gemini API key is correct
   - Check API quota and billing
   - Ensure environment variable is set properly

4. **Image analysis not working**
   - Requires valid Gemini API key
   - Check internet connection
   - Supported formats: PNG, JPG, JPEG

### Performance Tips

- Database storage improves performance for conversation history
- Image analysis may take a few seconds depending on image size
- Voice features work best in quiet environments

## Disclaimer

**Important**: This AI chatbot is NOT a replacement for professional therapy or medical advice.

- Designed for emotional support and general wellness conversations
- If experiencing serious mental health issues, consult a qualified professional
- In emergencies or with suicidal thoughts, contact local emergency services
- Conversations are processed by AI and should not contain sensitive personal information

## Support

For technical issues:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure environment variables are set properly
4. Check system requirements and compatibility

## License

This project is provided as-is for educational and personal use.

## Privacy and Data

- Conversations are stored locally (if database is configured)
- Image analysis is processed through Google's Gemini API
- No personal data is shared beyond what's necessary for AI processing
- Clear conversation history anytime using the "Clear Conversation" button