import re
from textblob import TextBlob
import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class EmotionDetector:
    def __init__(self):
        """Initialize emotion detection with multiple analysis methods"""
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Emotion keywords mapping
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'pleased', 'content', 'elated', 'thrilled', 'glad'],
            'sad': ['sad', 'depressed', 'down', 'blue', 'melancholy', 'gloomy', 'dejected', 'despondent', 'sorrowful', 'unhappy'],
            'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage', 'frustrated', 'upset', 'livid', 'enraged'],
            'anxious': ['anxious', 'worried', 'nervous', 'stressed', 'tense', 'uneasy', 'apprehensive', 'concerned', 'restless'],
            'fear': ['afraid', 'scared', 'terrified', 'frightened', 'panic', 'fearful', 'alarmed', 'intimidated'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'startled'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled']
        }
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def detect_emotion(self, text):
        """
        Detect emotion from text using multiple approaches
        Returns the most likely emotion
        """
        if not text or not text.strip():
            return 'neutral'
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Method 1: Keyword-based detection
        keyword_emotion = self._detect_by_keywords(cleaned_text)
        
        # Method 2: VADER sentiment analysis
        vader_emotion = self._detect_by_vader(text)
        
        # Method 3: TextBlob sentiment analysis
        textblob_emotion = self._detect_by_textblob(text)
        
        # Combine results with weights
        emotions = [keyword_emotion, vader_emotion, textblob_emotion]
        
        # If keyword detection found something specific, give it priority
        if keyword_emotion != 'neutral':
            return keyword_emotion
        
        # Otherwise, use sentiment analysis results
        if vader_emotion != 'neutral':
            return vader_emotion
        
        return textblob_emotion
    
    def _preprocess_text(self, text):
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _detect_by_keywords(self, text):
        """Detect emotion based on keyword matching"""
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences and apply weight based on word strength
                count = text.count(keyword)
                if count > 0:
                    score += count * (len(keyword) / 10)  # Longer words get more weight
            
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # Return emotion with highest score
            return max(emotion_scores, key=emotion_scores.get)
        
        return 'neutral'
    
    def _detect_by_vader(self, text):
        """Detect emotion using VADER sentiment analysis"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        # VADER returns compound, pos, neu, neg scores
        compound = scores['compound']
        pos = scores['pos']
        neg = scores['neg']
        
        # Map VADER scores to emotions
        if compound >= 0.5:
            return 'happy'
        elif compound <= -0.5:
            if neg > 0.6:
                return 'angry' if 'angry' in text.lower() or 'mad' in text.lower() else 'sad'
            else:
                return 'sad'
        elif compound > 0.1:
            return 'happy'
        elif compound < -0.1:
            return 'sad'
        else:
            return 'neutral'
    
    def _detect_by_textblob(self, text):
        """Detect emotion using TextBlob sentiment analysis"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Map polarity to emotions
            if polarity > 0.3:
                return 'happy'
            elif polarity < -0.3:
                return 'sad'
            elif subjectivity > 0.7:
                # High subjectivity might indicate anxiety or strong emotions
                if any(word in text.lower() for word in ['worry', 'stress', 'anxious', 'nervous']):
                    return 'anxious'
                elif any(word in text.lower() for word in ['angry', 'mad', 'frustrated']):
                    return 'angry'
            
            return 'neutral'
            
        except Exception:
            return 'neutral'
    
    def get_emotion_intensity(self, text):
        """Get the intensity of the detected emotion (0-1 scale)"""
        if not text or not text.strip():
            return 0.0
        
        try:
            # Use VADER compound score as intensity measure
            scores = self.vader_analyzer.polarity_scores(text)
            return abs(scores['compound'])
        except Exception:
            return 0.0
    
    def get_detailed_analysis(self, text):
        """Get detailed emotion analysis including confidence scores"""
        if not text or not text.strip():
            return {
                'primary_emotion': 'neutral',
                'intensity': 0.0,
                'confidence': 0.0,
                'all_emotions': {}
            }
        
        # Get all emotion scores
        emotion_scores = {}
        
        # Keyword-based scores
        cleaned_text = self._preprocess_text(text)
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                count = cleaned_text.count(keyword)
                if count > 0:
                    score += count
            emotion_scores[emotion] = score
        
        # VADER sentiment scores
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        try:
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
        except Exception:
            textblob_polarity = 0.0
        
        # Primary emotion
        primary_emotion = self.detect_emotion(text)
        intensity = self.get_emotion_intensity(text)
        
        # Calculate confidence based on consistency across methods
        confidence = min(1.0, intensity + 0.3) if primary_emotion != 'neutral' else 0.5
        
        return {
            'primary_emotion': primary_emotion,
            'intensity': intensity,
            'confidence': confidence,
            'all_emotions': emotion_scores,
            'vader_scores': vader_scores,
            'textblob_polarity': textblob_polarity
        }
