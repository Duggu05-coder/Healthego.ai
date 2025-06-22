import os
import json
import google.generativeai as genai
from datetime import datetime
from remedy_generator import RemedyGenerator

class TherapeuticAI:
    def __init__(self):
        """Initialize the therapeutic AI with Gemini Pro Vision API"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.remedy_generator = RemedyGenerator()
        
        # Therapeutic response templates based on emotions
        self.emotion_prompts = {
            'happy': "The user is expressing happiness. Help them savor this positive moment and suggest ways to maintain or build on this joy. Offer gratitude practices or ways to share positivity.",
            'sad': "The user is experiencing sadness. Provide immediate comfort techniques like breathing exercises, suggest gentle activities for mood lifting, and offer specific coping strategies for dealing with sadness.",
            'angry': "The user is expressing anger. Offer immediate anger management techniques like deep breathing or physical release exercises. Suggest constructive ways to process and channel this energy.",
            'anxious': "The user is showing signs of anxiety. Provide specific anxiety-reduction techniques like the 5-4-3-2-1 grounding method, breathing exercises, or progressive muscle relaxation. Offer practical steps to manage their worries.",
            'fear': "The user is expressing fear. Offer grounding techniques to help them feel safe, suggest ways to break down their fears into manageable parts, and provide courage-building exercises.",
            'surprise': "The user seems surprised or taken aback. Help them process this new information with mindfulness techniques and suggest ways to adapt to unexpected changes.",
            'disgust': "The user is expressing disgust or revulsion. Help them understand these feelings and suggest healthy ways to distance themselves from what's bothering them, including boundary-setting techniques.",
            'neutral': "The user's emotional state appears neutral. Use this as an opportunity to suggest proactive wellness practices, mindfulness exercises, or emotional awareness techniques."
        }
    
    def generate_response(self, user_message, detected_emotion, conversation_history=None):
        """
        Generate a therapeutic response based on user input and detected emotion
        """
        try:
            # Build the conversation context
            prompt = self._build_conversation_context(user_message, detected_emotion, conversation_history)
            
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.7,
                )
            )
            
            ai_response = response.text.strip()
            
            # Enhance response with specific remedies
            enhanced_response = self._enhance_with_remedies(ai_response, detected_emotion, user_message)
            
            # Ensure the response is appropriate and therapeutic
            return self._validate_and_enhance_response(enhanced_response, detected_emotion)
            
        except Exception as e:
            # Fallback response in case of API failure
            return self._get_fallback_response(detected_emotion, str(e))
    
    def _build_conversation_context(self, user_message, detected_emotion, conversation_history):
        """Build the conversation context for the AI"""
        
        # System prompt for therapeutic behavior
        system_prompt = """You are a compassionate and empathetic AI therapy assistant. Your role is to:

1. Provide emotional support and active listening
2. Offer practical, actionable coping strategies and remedies
3. Suggest specific techniques for managing emotions and situations
4. Give helpful advice based on therapeutic principles
5. Provide immediate tools and exercises the user can try
6. Never provide medical diagnoses or replace professional therapy

Guidelines for providing remedies and solutions:
- Always include at least one practical technique or exercise
- Offer specific breathing techniques, grounding exercises, or mindfulness practices
- Suggest behavioral changes or thought patterns to try
- Provide immediate actions they can take right now
- Include both short-term coping strategies and longer-term solutions
- Give concrete steps rather than just validation
- When appropriate, suggest journaling prompts or reflection exercises

Response structure:
1. Acknowledge their emotion and situation
2. Provide immediate practical remedy or technique
3. Offer additional coping strategies
4. End with encouragement and next steps

Remember: Focus on giving helpful, actionable advice while maintaining professional boundaries."""

        # Build conversation context
        context = system_prompt + "\n\n"
        
        # Add conversation history if available (last 3 exchanges to maintain context)
        if conversation_history:
            context += "Recent conversation:\n"
            recent_history = conversation_history[-6:]  # Last 3 user-assistant pairs
            for msg in recent_history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context += f"{role}: {msg['content']}\n"
            context += "\n"
        
        # Add emotion context
        emotion_context = self.emotion_prompts.get(detected_emotion, self.emotion_prompts['neutral'])
        
        # Current user message with emotion context
        context += f"""Emotion detected: {detected_emotion}
Context: {emotion_context}

User message: "{user_message}"

Please provide a helpful response that includes:
1. Acknowledgment of their emotional state
2. At least one immediate, practical technique they can try right now
3. Additional coping strategies or remedies for this situation
4. Encouraging next steps or actions they can take

Focus on giving actionable advice and specific techniques rather than just emotional validation."""

        return context
    
    def _validate_and_enhance_response(self, response, emotion):
        """Validate and enhance the AI response"""
        # Basic validation
        if not response or len(response.strip()) < 10:
            return self._get_fallback_response(emotion, "Response too short")
        
        # Ensure the response doesn't claim to be a real therapist
        problematic_phrases = [
            "as your therapist",
            "i am a therapist",
            "i'm a licensed",
            "i can diagnose",
            "my professional opinion"
        ]
        
        response_lower = response.lower()
        for phrase in problematic_phrases:
            if phrase in response_lower:
                response = response.replace(phrase, "as an AI assistant")
        
        # Add emotional validation if missing
        if not any(word in response_lower for word in ['understand', 'hear', 'feel', 'sounds', 'seems']):
            emotion_validation = self._get_emotion_validation(emotion)
            response = f"{emotion_validation} {response}"
        
        return response
    
    def _get_emotion_validation(self, emotion):
        """Get appropriate validation based on emotion"""
        validations = {
            'happy': "It's wonderful to hear the positivity in your message.",
            'sad': "I can sense that you're going through a difficult time.",
            'angry': "I understand that you're feeling frustrated right now.",
            'anxious': "It sounds like you're experiencing some worry or stress.",
            'fear': "I hear that you're feeling concerned about something.",
            'surprise': "It seems like something unexpected has happened.",
            'disgust': "I can tell that something is really bothering you.",
            'neutral': "Thank you for sharing your thoughts with me."
        }
        return validations.get(emotion, validations['neutral'])
    
    def _enhance_with_remedies(self, ai_response: str, emotion: str, user_message: str) -> str:
        """Enhance AI response with specific remedies"""
        try:
            # Get comprehensive remedies for this emotion
            remedies = self.remedy_generator.get_comprehensive_remedy(emotion)
            
            # Add immediate remedy to the response
            immediate_remedy = remedies['immediate'][0] if remedies['immediate'] else self.remedy_generator.get_quick_remedy(emotion)
            
            # Enhance the AI response with practical techniques
            enhanced_response = ai_response + f"\n\n**Here's something you can try right now:** {immediate_remedy}"
            
            # Add one additional technique if the response seems short
            if len(ai_response) < 100 and remedies['physical']:
                enhanced_response += f"\n\n**Physical technique:** {remedies['physical'][0]}"
            
            # For high-emotion situations, add more comprehensive help
            if emotion in ['anxious', 'sad', 'angry', 'fear'] and 'help' in user_message.lower():
                enhanced_response += f"\n\n{self.remedy_generator.format_remedy_response(emotion)}"
            
            return enhanced_response
            
        except Exception as e:
            # If remedy enhancement fails, return original response with a simple remedy
            quick_remedy = self.remedy_generator.get_quick_remedy(emotion)
            return ai_response + f"\n\nHere's a technique you can try: {quick_remedy}"
    
    def _get_fallback_response(self, emotion, error_message=None):
        """Provide fallback responses when AI generation fails"""
        fallback_responses = {
            'happy': "It's wonderful that you're feeling positive! Here's a simple technique to amplify this joy: Take a moment to write down three specific things that contributed to this happiness. This gratitude practice can help you recreate these positive experiences. Try sharing your joy with someone close to you - positive emotions grow when shared.",
            
            'sad': "I understand you're going through a difficult time. Here's an immediate technique that can help: Try the '4-7-8' breathing exercise - breathe in for 4 counts, hold for 7, exhale for 8. Repeat 3 times. Also, engage in gentle movement like a short walk, listen to comforting music, or do something kind for yourself today.",
            
            'angry': "I recognize your frustration. Here's an immediate anger management technique: Count slowly to 10 while taking deep breaths, or try progressive muscle relaxation - tense and release each muscle group. Physical exercise like walking or stretching can also help release this energy constructively. Consider writing your feelings down to process them.",
            
            'anxious': "I understand you're feeling anxious. Try this grounding technique right now: Look around and name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. Follow this with slow, deep breathing. For ongoing anxiety, try scheduling 'worry time' - 15 minutes daily to address concerns, then redirect your focus.",
            
            'fear': "I hear your concerns. Here's a technique to help: Practice the 'STOP' method - Stop what you're doing, Take a breath, Observe your thoughts and feelings, then Proceed with intention. Break down your fear into smaller, manageable parts. What's one small step you could take today to address this concern?",
            
            'surprise': "Unexpected events can be unsettling. Try this mindfulness technique: Place both feet on the ground, take three deep breaths, and remind yourself that adaptation is a strength. Journal about this experience to process it. Ask yourself: 'What can I learn from this?' and 'How can I adapt moving forward?'",
            
            'disgust': "Strong negative feelings need healthy outlets. Try this: First, remove yourself from the source if possible. Practice deep breathing, then engage in a cleansing activity like taking a shower, cleaning your space, or doing something that makes you feel refreshed. Set clear boundaries about what you will and won't accept.",
            
            'neutral': "This is a great time for proactive wellness. Try this mindfulness exercise: Set a timer for 5 minutes and focus on your breathing. Notice thoughts without judgment. Consider starting a daily gratitude practice or setting one small, positive intention for today. What's one thing you'd like to accomplish or experience today?"
        }
        
        return fallback_responses.get(emotion, fallback_responses['neutral'])
    
    def generate_coping_strategies(self, emotion, user_situation=None):
        """Generate specific coping strategies based on emotion and situation"""
        try:
            prompt = f"""You are a helpful AI assistant specializing in evidence-based coping strategies and emotional wellness techniques.

Based on the emotion '{emotion}' and the user's situation, provide 3-5 practical, evidence-based coping strategies. Keep each strategy concise and actionable.

Emotion: {emotion}
Situation context: {user_situation if user_situation else 'General emotional support needed'}

Please provide strategies in a numbered list format."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.5,
                )
            )
            
            return response.text.strip()
            
        except Exception:
            # Fallback coping strategies
            fallback_strategies = {
                'anxious': "1. Try deep breathing: Inhale for 4, hold for 4, exhale for 6\n2. Ground yourself using the 5-4-3-2-1 technique\n3. Take a short walk or do light stretching\n4. Write down your worries to externalize them",
                'sad': "1. Allow yourself to feel the emotion without judgment\n2. Reach out to a trusted friend or family member\n3. Engage in a small self-care activity\n4. Try gentle movement or listen to comforting music",
                'angry': "1. Take slow, deep breaths before responding\n2. Count to 10 or take a brief timeout\n3. Express your feelings through journaling\n4. Try progressive muscle relaxation",
                'happy': "1. Savor this positive moment mindfully\n2. Share your joy with someone you care about\n3. Write down what you're grateful for\n4. Use this energy for a creative activity"
            }
            return fallback_strategies.get(emotion, "Focus on deep breathing and grounding techniques. Remember that all emotions are temporary and valid.")
