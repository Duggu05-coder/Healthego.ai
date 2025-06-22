import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os

from emotion_detector import EmotionDetector
from therapeutic_ai import TherapeuticAI
from voice_handler import VoiceHandler
from session_manager import SessionManager
from image_analyzer import ImageAnalyzer

# Page configuration
st.set_page_config(
    page_title="AI Therapy Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()
if 'emotion_detector' not in st.session_state:
    st.session_state.emotion_detector = EmotionDetector()
if 'therapeutic_ai' not in st.session_state:
    st.session_state.therapeutic_ai = TherapeuticAI()
if 'voice_handler' not in st.session_state:
    st.session_state.voice_handler = VoiceHandler()
if 'voice_mode' not in st.session_state:
    st.session_state.voice_mode = False
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'image_analyzer' not in st.session_state:
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        st.session_state.image_analyzer = ImageAnalyzer(gemini_key)
    else:
        st.session_state.image_analyzer = None

def main():
    # Header
    st.title("🤖 AI Therapy Chatbot")
    st.markdown("---")
    
    # Disclaimer
    with st.expander("⚠️ Important Disclaimer - Please Read"):
        st.warning("""
        **This AI chatbot is NOT a replacement for professional therapy or medical advice.**
        
        - This tool is designed for emotional support and general wellness conversations
        - If you're experiencing serious mental health issues, please consult a qualified mental health professional
        - In case of emergency or suicidal thoughts, contact your local emergency services immediately
        - Your conversations are processed by AI and should not contain sensitive personal information
        
        By using this chatbot, you acknowledge that you understand these limitations.
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("Controls")
        
        # Voice mode toggle (only show if microphone is available)
        if st.session_state.voice_handler.microphone_available:
            voice_mode = st.toggle("🎤 Voice Mode", value=st.session_state.voice_mode)
            st.session_state.voice_mode = voice_mode
            
            if voice_mode:
                st.info("Voice mode enabled. Use the microphone button to record your message.")
        else:
            st.session_state.voice_mode = False
            st.info("🎤 Voice input not available in this environment. Text-to-speech still works for responses.")
        
        st.markdown("---")
        
        # Emotion tracking visualization
        st.subheader("📊 Emotion Tracking")
        emotions_data = st.session_state.session_manager.get_emotions_summary()
        
        if emotions_data:
            # Create emotion chart
            df = pd.DataFrame(list(emotions_data.items()), columns=['Emotion', 'Count'])
            fig = px.pie(df, values='Count', names='Emotion', title="Session Emotions")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start chatting to see emotion tracking!")
        
        st.markdown("---")
        
        # Session controls
        st.subheader("🔧 Session")
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.session_manager.clear_session()
            st.rerun()
        
        # Conversation stats
        stats = st.session_state.session_manager.get_session_stats()
        st.metric("Messages", stats['message_count'])
        st.metric("Session Duration", f"{stats['duration_minutes']:.1f} min")
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat history
        st.subheader("💬 Conversation")
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            messages = st.session_state.session_manager.get_messages()
            
            for msg in messages:
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(msg['content'])
                        if 'emotion' in msg:
                            emotion_color = get_emotion_color(msg['emotion'])
                            st.markdown(f"<span style='color: {emotion_color}; font-size: 0.8em;'>Detected emotion: {msg['emotion']}</span>", unsafe_allow_html=True)
                        st.caption(msg['timestamp'])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg['content'])
                        st.caption(msg['timestamp'])
                        
                        # Audio playback button for AI responses
                        if 'audio_file' in msg and os.path.exists(msg['audio_file']):
                            with open(msg['audio_file'], 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format='audio/wav')
        
        # Input section
        st.markdown("---")
        
        # Quick remedy buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("😰 Need Help with Anxiety"):
                process_user_input("I'm feeling anxious and need immediate help with coping techniques")
        with col2:
            if st.button("😢 Feeling Down"):
                process_user_input("I'm feeling sad and need some support and strategies to feel better")
        with col3:
            if st.button("😠 Managing Anger"):
                process_user_input("I'm feeling angry and need help managing these emotions constructively")
        
        # Image upload section
        st.markdown("### 📸 Share an Image")
        uploaded_file = st.file_uploader(
            "Upload an image to discuss how it makes you feel",
            type=['png', 'jpg', 'jpeg'],
            help="Share photos, artwork, or any image that represents your current mood or situation"
        )
        
        if uploaded_file is not None and not st.session_state.processing:
            if st.button("Analyze Image"):
                process_image_input(uploaded_file)
        
        if not st.session_state.voice_mode:
            # Text input mode
            user_input = st.chat_input("Type your message here...")
            
            if user_input and not st.session_state.processing:
                process_user_input(user_input)
        
        else:
            # Voice input mode
            col_record, col_stop = st.columns(2)
            
            with col_record:
                if st.button("🎤 Start Recording", disabled=st.session_state.processing):
                    process_voice_input()
            
            with col_stop:
                if st.button("⏹️ Stop & Process", disabled=not st.session_state.processing):
                    st.session_state.processing = False
                    st.rerun()
    
    with col2:
        # Real-time emotion indicator
        st.subheader("😊 Current Mood")
        current_emotion = st.session_state.session_manager.get_current_emotion()
        
        if current_emotion:
            emotion_emoji = get_emotion_emoji(current_emotion)
            emotion_color = get_emotion_color(current_emotion)
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: {emotion_color}20;'>
                <div style='font-size: 3em;'>{emotion_emoji}</div>
                <div style='font-size: 1.2em; color: {emotion_color}; font-weight: bold;'>{current_emotion.title()}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Share your thoughts or an image to detect emotions!")
        
        # Image analysis features info
        st.markdown("---")
        st.subheader("🖼️ Image Analysis")
        st.info("Upload images to:")
        st.write("• Analyze emotional content")
        st.write("• Get mood-based support")
        st.write("• Receive visual therapy suggestions")
        st.write("• Express feelings through imagery")

def process_user_input(user_input):
    """Process user text input"""
    st.session_state.processing = True
    
    try:
        # Detect emotion
        emotion = st.session_state.emotion_detector.detect_emotion(user_input)
        
        # Add user message to session
        st.session_state.session_manager.add_message('user', user_input, emotion=emotion)
        
        # Generate AI response
        conversation_history = st.session_state.session_manager.get_conversation_context()
        ai_response = st.session_state.therapeutic_ai.generate_response(
            user_input, emotion, conversation_history
        )
        
        # Generate audio for AI response if voice mode is enabled
        audio_file = None
        if st.session_state.voice_mode:
            audio_file = st.session_state.voice_handler.text_to_speech(ai_response)
        
        # Add AI response to session
        st.session_state.session_manager.add_message('assistant', ai_response, audio_file=audio_file)
        
    except Exception as e:
        st.error(f"Error processing your message: {str(e)}")
    
    finally:
        st.session_state.processing = False
        st.rerun()

def process_voice_input():
    """Process voice input"""
    st.session_state.processing = True
    
    try:
        with st.spinner("Listening... Speak now!"):
            # Record audio
            audio_text = st.session_state.voice_handler.speech_to_text()
            
            if audio_text:
                # Process the transcribed text
                process_user_input(audio_text)
            else:
                st.warning("Could not understand the audio. Please try again.")
                st.session_state.processing = False
    
    except Exception as e:
        st.error(f"Voice input error: {str(e)}")
        st.session_state.processing = False

def get_emotion_emoji(emotion):
    """Get emoji for emotion"""
    emoji_map = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'anxious': '😰',
        'fear': '😨',
        'surprise': '😲',
        'disgust': '🤢',
        'neutral': '😐'
    }
    return emoji_map.get(emotion.lower(), '😐')

def process_image_input(uploaded_file):
    """Process uploaded image input"""
    if not st.session_state.image_analyzer:
        st.error("Image analysis not available. Please check Gemini API configuration.")
        return
    
    st.session_state.processing = True
    
    try:
        with st.spinner("Analyzing your image..."):
            # Display the uploaded image
            image = uploaded_file
            st.image(image, caption="Your uploaded image", use_column_width=True)
            
            # Analyze the image
            image_analysis = st.session_state.image_analyzer.analyze_image_emotion(image)
            
            # Get therapeutic content analysis
            therapeutic_analysis = st.session_state.image_analyzer.analyze_image_content(image)
            
            # Detect faces if any
            face_detection = st.session_state.image_analyzer.detect_faces_and_emotions(image)
            
            # Generate AI response based on image
            ai_response = st.session_state.image_analyzer.generate_image_based_response(image_analysis)
            
            # Add user message about sharing image
            emotion = image_analysis['emotion']
            user_message = f"I shared an image that shows {emotion} emotions"
            st.session_state.session_manager.add_message('user', user_message, emotion=emotion)
            
            # Enhance AI response with remedies
            conversation_history = st.session_state.session_manager.get_conversation_context()
            enhanced_response = st.session_state.therapeutic_ai.generate_response(
                user_message, emotion, conversation_history
            )
            
            # Combine responses
            full_response = f"""Based on your image, I can see {image_analysis['analysis']}

{enhanced_response}

**Image Analysis Insights:**
{therapeutic_analysis}

**Additional Suggestions:**
"""
            
            # Add specific suggestions
            suggestions = st.session_state.image_analyzer.get_image_therapy_suggestions(emotion, image_analysis)
            for suggestion in suggestions:
                full_response += f"• {suggestion}\n"
            
            # Add AI response to session
            st.session_state.session_manager.add_message('assistant', full_response)
            
            # Show face detection results if faces found
            if face_detection['faces_detected'] > 0:
                st.info(f"Detected {face_detection['faces_detected']} face(s) in the image, which helps with emotional analysis.")
            
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
    
    finally:
        st.session_state.processing = False
        st.rerun()

def get_emotion_color(emotion):
    """Get color for emotion"""
    color_map = {
        'happy': '#4CAF50',
        'sad': '#2196F3',
        'angry': '#F44336',
        'anxious': '#FF9800',
        'fear': '#9C27B0',
        'surprise': '#FFEB3B',
        'disgust': '#795548',
        'neutral': '#9E9E9E'
    }
    return color_map.get(emotion.lower(), '#9E9E9E')

# Call main function directly
main()
