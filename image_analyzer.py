import base64
import io
import google.generativeai as genai
from PIL import Image
import streamlit as st
import cv2
import numpy as np

class ImageAnalyzer:
    def __init__(self, gemini_api_key):
        """Initialize image analyzer with Gemini Pro Vision"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
        # Emotion keywords to help detect emotional content in images
        self.emotion_keywords = {
            'happy': ['smile', 'laughing', 'joy', 'celebration', 'bright', 'cheerful', 'excited'],
            'sad': ['crying', 'tears', 'frown', 'gloomy', 'dark', 'melancholy', 'upset'],
            'angry': ['frown', 'scowl', 'aggressive', 'tense', 'clenched', 'furious'],
            'anxious': ['worried', 'nervous', 'tense', 'stressed', 'fidgeting', 'restless'],
            'fear': ['scared', 'frightened', 'terrified', 'hiding', 'defensive'],
            'surprise': ['shocked', 'amazed', 'startled', 'wide-eyed', 'unexpected'],
            'neutral': ['calm', 'peaceful', 'serene', 'relaxed', 'content']
        }
    
    def analyze_image_emotion(self, image_file):
        """Analyze emotional content in an image"""
        try:
            # Convert uploaded file to PIL Image
            image = Image.open(image_file)
            
            # Prepare the prompt for emotional analysis
            prompt = """Analyze this image for emotional content. Consider:
            1. Facial expressions and body language
            2. Colors, lighting, and mood of the scene
            3. Objects or symbols that might convey emotions
            4. Overall atmosphere and feeling
            
            Identify the primary emotion conveyed (happy, sad, angry, anxious, fear, surprise, neutral) and explain why.
            Also provide a brief description of what you see in the image.
            
            Format your response as:
            Emotion: [primary emotion]
            Confidence: [high/medium/low]
            Description: [what you see]
            Emotional indicators: [specific visual cues that indicate this emotion]"""
            
            # Generate analysis using Gemini Pro Vision
            response = self.model.generate_content([prompt, image])
            analysis_text = response.text
            
            # Parse the response to extract emotion
            emotion = self._extract_emotion_from_analysis(analysis_text)
            
            return {
                'emotion': emotion,
                'analysis': analysis_text,
                'confidence': self._extract_confidence(analysis_text)
            }
            
        except Exception as e:
            return {
                'emotion': 'neutral',
                'analysis': f"Unable to analyze image: {str(e)}",
                'confidence': 'low'
            }
    
    def analyze_image_content(self, image_file, user_context=None):
        """Analyze image content for therapeutic context"""
        try:
            image = Image.open(image_file)
            
            context_prompt = ""
            if user_context:
                context_prompt = f"The user shared this context: '{user_context}'"
            
            prompt = f"""As an AI therapy assistant, analyze this image in the context of emotional wellbeing. 
            {context_prompt}
            
            Please provide:
            1. A compassionate description of what you see
            2. Any emotional themes or feelings the image might represent
            3. Therapeutic observations about what this image might mean to someone
            4. Supportive insights or reflections
            
            Be empathetic and focus on emotional support rather than just description."""
            
            response = self.model.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            return f"I can see you've shared an image with me. While I had trouble analyzing the specific details, I'm here to support you. Would you like to tell me about what this image means to you or how it makes you feel?"
    
    def _extract_emotion_from_analysis(self, analysis_text):
        """Extract primary emotion from analysis text"""
        analysis_lower = analysis_text.lower()
        
        # Look for explicit emotion mentions
        for emotion, keywords in self.emotion_keywords.items():
            if f"emotion: {emotion}" in analysis_lower:
                return emotion
            
            # Count keyword matches
            keyword_count = sum(1 for keyword in keywords if keyword in analysis_lower)
            if keyword_count >= 2:  # If multiple keywords match
                return emotion
        
        # Default fallback
        if any(word in analysis_lower for word in ['happy', 'joy', 'smile', 'positive']):
            return 'happy'
        elif any(word in analysis_lower for word in ['sad', 'cry', 'tear', 'down']):
            return 'sad'
        elif any(word in analysis_lower for word in ['angry', 'mad', 'furious', 'aggressive']):
            return 'angry'
        elif any(word in analysis_lower for word in ['anxious', 'worry', 'nervous', 'stress']):
            return 'anxious'
        elif any(word in analysis_lower for word in ['fear', 'scared', 'afraid', 'frightened']):
            return 'fear'
        elif any(word in analysis_lower for word in ['surprise', 'shock', 'amaze', 'startled']):
            return 'surprise'
        else:
            return 'neutral'
    
    def _extract_confidence(self, analysis_text):
        """Extract confidence level from analysis"""
        analysis_lower = analysis_text.lower()
        if 'confidence: high' in analysis_lower:
            return 'high'
        elif 'confidence: medium' in analysis_lower:
            return 'medium'
        elif 'confidence: low' in analysis_lower:
            return 'low'
        else:
            return 'medium'  # default
    
    def generate_image_based_response(self, image_analysis, user_message=None):
        """Generate therapeutic response based on image analysis"""
        emotion = image_analysis['emotion']
        analysis = image_analysis['analysis']
        
        try:
            context = user_message if user_message else "The user has shared an image"
            
            prompt = f"""As a compassionate AI therapy assistant, respond to this situation:
            
            User context: {context}
            Image analysis: {analysis}
            Detected emotion: {emotion}
            
            Provide a therapeutic response that:
            1. Acknowledges what they've shared through the image
            2. Validates their emotions
            3. Offers specific, practical support techniques
            4. Encourages further discussion if appropriate
            
            Be warm, empathetic, and solution-focused."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Thank you for sharing this image with me. I can sense there are emotions connected to what you've shown me. Sometimes images can express feelings that are hard to put into words. Would you like to tell me more about what this image represents for you or how it makes you feel?"
    
    def detect_faces_and_emotions(self, image_file):
        """Detect faces in image using OpenCV (basic emotion detection)"""
        try:
            # Convert PIL image to OpenCV format
            image = Image.open(image_file)
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Load face detection cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return {
                'faces_detected': len(faces),
                'face_locations': faces.tolist() if len(faces) > 0 else []
            }
            
        except Exception as e:
            return {
                'faces_detected': 0,
                'face_locations': [],
                'error': str(e)
            }
    
    def get_image_therapy_suggestions(self, emotion, image_context):
        """Get specific therapy suggestions based on image content and detected emotion"""
        suggestions = {
            'happy': [
                "Consider creating a gratitude journal with images that bring you joy",
                "Use this positive feeling as motivation for challenging tasks",
                "Share this happiness with someone who might need it today"
            ],
            'sad': [
                "Looking at meaningful images can be therapeutic - consider creating a comfort photo album",
                "Sometimes expressing sadness through visual art or photography can be healing",
                "If this image represents a loss, remember that grief is a natural process"
            ],
            'angry': [
                "Channel this energy into creative expression through art or photography",
                "Consider what this image represents and how you can address the underlying issue",
                "Physical exercise might help process these intense feelings"
            ],
            'anxious': [
                "Create a calming image collection for when anxiety strikes",
                "Practice mindful observation of peaceful images",
                "Consider what in this image triggers anxiety and how to address it"
            ],
            'fear': [
                "Gradual exposure to feared images can help build resilience over time",
                "Focus on images that represent safety and comfort",
                "Consider talking to someone about what this image represents for you"
            ],
            'neutral': [
                "Use neutral images for mindfulness meditation practices",
                "Consider what emotions this image might represent for you personally",
                "Visual journaling can be a powerful tool for self-reflection"
            ]
        }
        
        return suggestions.get(emotion, suggestions['neutral'])