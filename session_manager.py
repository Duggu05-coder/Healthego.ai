import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import streamlit as st
from database import DatabaseManager

class SessionManager:
    def __init__(self):
        """Initialize session manager with database support"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        
        # Initialize database manager
        try:
            self.db = DatabaseManager()
            # Create user session in database
            self.db.create_user_session(st.session_state.session_id)
            
            # Load existing data from database
            if 'messages' not in st.session_state:
                st.session_state.messages = self.db.get_conversation_history(st.session_state.session_id)
            
            if 'emotions_history' not in st.session_state:
                st.session_state.emotions_history = self.db.get_emotion_timeline(st.session_state.session_id)
                
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            # Fallback to in-memory storage
            self.db = None
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            if 'emotions_history' not in st.session_state:
                st.session_state.emotions_history = []
    
    def add_message(self, role, content, emotion=None, audio_file=None):
        """Add a message to the conversation history"""
        message_id = str(uuid.uuid4())
        message = {
            'id': message_id,
            'message_id': message_id,
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'datetime': datetime.now()
        }
        
        if emotion and role == 'user':
            message['emotion'] = emotion
            # Track emotion history
            emotion_entry = {
                'emotion': emotion,
                'timestamp': datetime.now(),
                'message_id': message_id
            }
            st.session_state.emotions_history.append(emotion_entry)
            
            # Save emotion to database
            if self.db:
                try:
                    self.db.save_emotion(
                        st.session_state.session_id,
                        message_id,
                        emotion,
                        detection_method='multi_method'
                    )
                except Exception as e:
                    st.warning(f"Failed to save emotion to database: {str(e)}")
        
        if audio_file:
            message['audio_file'] = audio_file
        
        # Save message to database
        if self.db:
            try:
                self.db.save_message(
                    st.session_state.session_id,
                    message_id,
                    role,
                    content,
                    emotion,
                    audio_file_path=audio_file
                )
            except Exception as e:
                st.warning(f"Failed to save message to database: {str(e)}")
        
        st.session_state.messages.append(message)
        
        # Limit message history to prevent memory issues (keep last 50 messages)
        if len(st.session_state.messages) > 50:
            st.session_state.messages = st.session_state.messages[-50:]
    
    def get_messages(self):
        """Get all messages in the current session"""
        return st.session_state.messages
    
    def get_conversation_context(self, max_messages=10):
        """Get recent conversation context for AI"""
        messages = st.session_state.messages
        if len(messages) <= max_messages:
            return messages
        return messages[-max_messages:]
    
    def get_current_emotion(self):
        """Get the most recent emotion detected"""
        if self.db:
            try:
                return self.db.get_current_emotion(st.session_state.session_id)
            except Exception:
                pass
        
        if not st.session_state.emotions_history:
            return None
        
        # Return the most recent emotion
        return st.session_state.emotions_history[-1]['emotion']
    
    def get_emotions_summary(self):
        """Get a summary of emotions in the current session"""
        if self.db:
            try:
                return self.db.get_emotion_summary(st.session_state.session_id)
            except Exception:
                pass
        
        if not st.session_state.emotions_history:
            return {}
        
        emotions = [entry['emotion'] for entry in st.session_state.emotions_history]
        return dict(Counter(emotions))
    
    def get_emotion_timeline(self):
        """Get emotion timeline for visualization"""
        if not st.session_state.emotions_history:
            return []
        
        timeline = []
        for entry in st.session_state.emotions_history:
            timeline.append({
                'emotion': entry['emotion'],
                'timestamp': entry['timestamp'],
                'time_str': entry['timestamp'].strftime("%H:%M:%S")
            })
        
        return timeline
    
    def get_session_stats(self):
        """Get session statistics"""
        current_time = datetime.now()
        session_duration = current_time - st.session_state.session_start_time
        
        message_count = len(st.session_state.messages)
        user_messages = len([msg for msg in st.session_state.messages if msg['role'] == 'user'])
        ai_messages = len([msg for msg in st.session_state.messages if msg['role'] == 'assistant'])
        
        emotions_detected = len(st.session_state.emotions_history)
        unique_emotions = len(set(entry['emotion'] for entry in st.session_state.emotions_history))
        
        return {
            'session_id': st.session_state.session_id,
            'duration_minutes': session_duration.total_seconds() / 60,
            'message_count': message_count,
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'emotions_detected': emotions_detected,
            'unique_emotions': unique_emotions,
            'session_start': st.session_state.session_start_time,
            'current_time': current_time
        }
    
    def clear_session(self):
        """Clear the current session and start fresh"""
        # Clear database data
        if self.db:
            try:
                self.db.clear_session_data(st.session_state.session_id)
            except Exception as e:
                st.warning(f"Failed to clear database session: {str(e)}")
        
        # Clear session state
        st.session_state.messages = []
        st.session_state.emotions_history = []
        st.session_state.session_start_time = datetime.now()
        old_session_id = st.session_state.session_id
        st.session_state.session_id = str(uuid.uuid4())
        
        # Create new session in database
        if self.db:
            try:
                self.db.create_user_session(st.session_state.session_id)
            except Exception as e:
                st.warning(f"Failed to create new database session: {str(e)}")
    
    def export_conversation(self):
        """Export conversation history as a dictionary"""
        stats = self.get_session_stats()
        emotions_summary = self.get_emotions_summary()
        
        export_data = {
            'session_info': {
                'session_id': stats['session_id'],
                'start_time': stats['session_start'].isoformat(),
                'duration_minutes': stats['duration_minutes'],
                'message_count': stats['message_count']
            },
            'emotions_summary': emotions_summary,
            'conversation': []
        }
        
        for msg in st.session_state.messages:
            conversation_entry = {
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp']
            }
            
            if 'emotion' in msg:
                conversation_entry['emotion'] = msg['emotion']
            
            export_data['conversation'].append(conversation_entry)
        
        return export_data
    
    def get_emotional_insights(self):
        """Generate insights about emotional patterns"""
        if not st.session_state.emotions_history:
            return {
                'insights': ["No emotional data available yet. Continue chatting to see insights!"],
                'dominant_emotion': None,
                'emotion_changes': 0
            }
        
        emotions = [entry['emotion'] for entry in st.session_state.emotions_history]
        emotion_counts = Counter(emotions)
        
        # Dominant emotion
        dominant_emotion = emotion_counts.most_common(1)[0][0]
        dominant_count = emotion_counts.most_common(1)[0][1]
        
        # Emotion changes (transitions)
        emotion_changes = 0
        for i in range(1, len(emotions)):
            if emotions[i] != emotions[i-1]:
                emotion_changes += 1
        
        # Generate insights
        insights = []
        
        total_emotions = len(emotions)
        
        # Dominant emotion insight
        percentage = (dominant_count / total_emotions) * 100
        insights.append(f"Your dominant emotion this session has been '{dominant_emotion}' ({percentage:.1f}% of the time)")
        
        # Emotional variety insight
        unique_emotions = len(set(emotions))
        if unique_emotions > 3:
            insights.append(f"You've experienced a wide range of emotions ({unique_emotions} different types)")
        elif unique_emotions == 1:
            insights.append("You've maintained a consistent emotional state throughout our conversation")
        
        # Emotional stability insight
        if emotion_changes > total_emotions * 0.7:
            insights.append("You've shown significant emotional fluctuation during our conversation")
        elif emotion_changes < total_emotions * 0.3:
            insights.append("You've maintained relatively stable emotions during our conversation")
        
        # Recent emotion trend
        if len(emotions) >= 3:
            recent_emotions = emotions[-3:]
            if len(set(recent_emotions)) == 1:
                insights.append(f"Your recent messages consistently show '{recent_emotions[0]}' emotions")
        
        return {
            'insights': insights,
            'dominant_emotion': dominant_emotion,
            'emotion_changes': emotion_changes,
            'emotional_variety': unique_emotions,
            'total_interactions': total_emotions
        }
    
    def get_time_based_patterns(self):
        """Analyze emotional patterns over time"""
        if not st.session_state.emotions_history:
            return {}
        
        # Group emotions by time periods
        emotion_timeline = []
        for entry in st.session_state.emotions_history:
            emotion_timeline.append({
                'emotion': entry['emotion'],
                'minutes_since_start': (entry['timestamp'] - st.session_state.session_start_time).total_seconds() / 60
            })
        
        return {
            'timeline': emotion_timeline,
            'session_duration': (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
        }
