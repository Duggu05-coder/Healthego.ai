import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import streamlit as st

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(String(255), nullable=False)
    message_id = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    emotion = Column(String(50), nullable=True)
    emotion_confidence = Column(Float, nullable=True)
    audio_file_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class EmotionHistory(Base):
    __tablename__ = 'emotion_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(String(255), nullable=False)
    message_id = Column(String(255), nullable=False)
    emotion = Column(String(50), nullable=False)
    intensity = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    detection_method = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SessionStats(Base):
    __tablename__ = 'session_stats'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_session_id = Column(String(255), unique=True, nullable=False)
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    ai_messages = Column(Integer, default=0)
    emotions_detected = Column(Integer, default=0)
    unique_emotions = Column(Integer, default=0)
    session_duration_minutes = Column(Float, default=0.0)
    dominant_emotion = Column(String(50), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_db_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_user_session(self, session_id: str):
        """Create or update user session"""
        db = self.get_db_session()
        try:
            # Check if user exists
            user = db.query(User).filter(User.session_id == session_id).first()
            if not user:
                user = User(session_id=session_id)
                db.add(user)
            else:
                user.last_active = datetime.utcnow()
            
            # Create or update session stats
            stats = db.query(SessionStats).filter(SessionStats.user_session_id == session_id).first()
            if not stats:
                stats = SessionStats(user_session_id=session_id)
                db.add(stats)
            
            db.commit()
            return user.id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def save_message(self, user_session_id: str, message_id: str, role: str, content: str, 
                    emotion: str = None, emotion_confidence: float = None, audio_file_path: str = None):
        """Save conversation message"""
        db = self.get_db_session()
        try:
            message = Conversation(
                user_session_id=user_session_id,
                message_id=message_id,
                role=role,
                content=content,
                emotion=emotion,
                emotion_confidence=emotion_confidence,
                audio_file_path=audio_file_path
            )
            db.add(message)
            
            # Update session stats
            self._update_session_stats(db, user_session_id, role, emotion)
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def save_emotion(self, user_session_id: str, message_id: str, emotion: str, 
                    intensity: float = None, confidence: float = None, detection_method: str = None):
        """Save emotion detection data"""
        db = self.get_db_session()
        try:
            emotion_entry = EmotionHistory(
                user_session_id=user_session_id,
                message_id=message_id,
                emotion=emotion,
                intensity=intensity,
                confidence=confidence,
                detection_method=detection_method
            )
            db.add(emotion_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_conversation_history(self, user_session_id: str, limit: int = 50):
        """Get conversation history for a user session"""
        db = self.get_db_session()
        try:
            messages = db.query(Conversation).filter(
                Conversation.user_session_id == user_session_id
            ).order_by(Conversation.timestamp.desc()).limit(limit).all()
            
            return [{
                'id': str(msg.id),
                'message_id': msg.message_id,
                'role': msg.role,
                'content': msg.content,
                'emotion': msg.emotion,
                'emotion_confidence': msg.emotion_confidence,
                'audio_file_path': msg.audio_file_path,
                'timestamp': msg.timestamp.strftime("%H:%M:%S"),
                'datetime': msg.timestamp
            } for msg in reversed(messages)]
        finally:
            db.close()
    
    def get_emotion_summary(self, user_session_id: str):
        """Get emotion summary for a user session"""
        db = self.get_db_session()
        try:
            emotions = db.query(EmotionHistory.emotion).filter(
                EmotionHistory.user_session_id == user_session_id
            ).all()
            
            emotion_counts = {}
            for emotion in emotions:
                emotion_name = emotion[0]
                emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
            
            return emotion_counts
        finally:
            db.close()
    
    def get_session_statistics(self, user_session_id: str):
        """Get session statistics"""
        db = self.get_db_session()
        try:
            stats = db.query(SessionStats).filter(
                SessionStats.user_session_id == user_session_id
            ).first()
            
            if not stats:
                return {
                    'total_messages': 0,
                    'user_messages': 0,
                    'ai_messages': 0,
                    'emotions_detected': 0,
                    'unique_emotions': 0,
                    'session_duration_minutes': 0.0,
                    'dominant_emotion': None
                }
            
            return {
                'total_messages': stats.total_messages,
                'user_messages': stats.user_messages,
                'ai_messages': stats.ai_messages,
                'emotions_detected': stats.emotions_detected,
                'unique_emotions': stats.unique_emotions,
                'session_duration_minutes': stats.session_duration_minutes,
                'dominant_emotion': stats.dominant_emotion
            }
        finally:
            db.close()
    
    def get_current_emotion(self, user_session_id: str):
        """Get the most recent emotion for a user session"""
        db = self.get_db_session()
        try:
            latest_emotion = db.query(EmotionHistory).filter(
                EmotionHistory.user_session_id == user_session_id
            ).order_by(EmotionHistory.timestamp.desc()).first()
            
            return latest_emotion.emotion if latest_emotion else None
        finally:
            db.close()
    
    def clear_session_data(self, user_session_id: str):
        """Clear all data for a user session"""
        db = self.get_db_session()
        try:
            # Delete conversations
            db.query(Conversation).filter(
                Conversation.user_session_id == user_session_id
            ).delete()
            
            # Delete emotion history
            db.query(EmotionHistory).filter(
                EmotionHistory.user_session_id == user_session_id
            ).delete()
            
            # Reset session stats
            stats = db.query(SessionStats).filter(
                SessionStats.user_session_id == user_session_id
            ).first()
            if stats:
                stats.total_messages = 0
                stats.user_messages = 0
                stats.ai_messages = 0
                stats.emotions_detected = 0
                stats.unique_emotions = 0
                stats.session_duration_minutes = 0.0
                stats.dominant_emotion = None
                stats.last_updated = datetime.utcnow()
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _update_session_stats(self, db, user_session_id: str, role: str, emotion: str = None):
        """Update session statistics"""
        stats = db.query(SessionStats).filter(
            SessionStats.user_session_id == user_session_id
        ).first()
        
        if stats:
            stats.total_messages += 1
            if role == 'user':
                stats.user_messages += 1
                if emotion:
                    stats.emotions_detected += 1
            elif role == 'assistant':
                stats.ai_messages += 1
            
            # Calculate unique emotions
            unique_emotions = db.query(EmotionHistory.emotion).filter(
                EmotionHistory.user_session_id == user_session_id
            ).distinct().count()
            stats.unique_emotions = unique_emotions
            
            # Calculate dominant emotion
            emotion_counts = db.query(
                EmotionHistory.emotion,
                db.func.count(EmotionHistory.emotion).label('count')
            ).filter(
                EmotionHistory.user_session_id == user_session_id
            ).group_by(EmotionHistory.emotion).order_by(db.text('count DESC')).first()
            
            if emotion_counts:
                stats.dominant_emotion = emotion_counts[0]
            
            stats.last_updated = datetime.utcnow()
    
    def get_emotion_timeline(self, user_session_id: str):
        """Get emotion timeline for visualization"""
        db = self.get_db_session()
        try:
            emotions = db.query(EmotionHistory).filter(
                EmotionHistory.user_session_id == user_session_id
            ).order_by(EmotionHistory.timestamp.asc()).all()
            
            return [{
                'emotion': emotion.emotion,
                'intensity': emotion.intensity,
                'confidence': emotion.confidence,
                'timestamp': emotion.timestamp,
                'time_str': emotion.timestamp.strftime("%H:%M:%S")
            } for emotion in emotions]
        finally:
            db.close()