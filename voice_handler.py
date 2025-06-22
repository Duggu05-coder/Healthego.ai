import os
import tempfile
import time
from io import BytesIO
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import streamlit as st

class VoiceHandler:
    def __init__(self):
        """Initialize voice handling components"""
        self.recognizer = sr.Recognizer()
        self.microphone_available = False
        self.microphone = None
        
        # Try to initialize microphone, but don't fail if not available
        try:
            self.microphone = sr.Microphone()
            self.microphone_available = True
        except Exception as e:
            st.info("Voice input not available in this environment. Text-to-speech will still work.")
            self.microphone_available = False
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            self.use_pyttsx3 = True
        except Exception:
            self.use_pyttsx3 = False
            # Don't show warning on every initialization
        
        # Adjust for ambient noise only if microphone is available
        if self.microphone_available:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except Exception as e:
                st.warning(f"Could not adjust for ambient noise: {e}")
                self.microphone_available = False
    
    def speech_to_text(self, timeout=5, phrase_time_limit=10):
        """
        Convert speech to text using the microphone
        Returns the transcribed text or None if failed
        """
        if not self.microphone_available:
            st.error("Voice input is not available in this environment. Please use text input instead.")
            return None
            
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Please speak now!")
                
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                st.info("🔄 Processing speech...")
                
                # Try multiple recognition services for better accuracy
                text = None
                
                # Try Google Speech Recognition first (most accurate)
                try:
                    text = self.recognizer.recognize_google(audio)
                    st.success("✅ Speech recognized successfully!")
                    return text
                except sr.RequestError:
                    st.warning("Google Speech Recognition service unavailable")
                except sr.UnknownValueError:
                    pass
                
                # Fallback to offline recognition if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    st.success("✅ Speech recognized (offline)!")
                    return text
                except (sr.RequestError, sr.UnknownValueError):
                    pass
                
                # If all methods fail
                st.error("❌ Could not understand the audio. Please try speaking clearly.")
                return None
                
        except sr.WaitTimeoutError:
            st.warning("⏱️ Listening timeout. Please try again.")
            return None
        except Exception as e:
            st.error(f"❌ Speech recognition error: {str(e)}")
            return None
    
    def text_to_speech(self, text, save_to_file=True):
        """
        Convert text to speech
        Returns the path to the audio file if save_to_file=True, otherwise plays directly
        """
        if not text or not text.strip():
            return None
        
        try:
            if save_to_file:
                return self._save_speech_to_file(text)
            else:
                self._play_speech_direct(text)
                return None
                
        except Exception as e:
            st.error(f"Text-to-speech error: {str(e)}")
            return None
    
    def _save_speech_to_file(self, text):
        """Save speech to a temporary audio file"""
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            if self.use_pyttsx3:
                # Use pyttsx3 for offline TTS
                self.tts_engine.save_to_file(text, temp_file.name)
                self.tts_engine.runAndWait()
            else:
                # Use gTTS for online TTS
                tts = gTTS(text=text, lang='en', slow=False)
                
                # Save to temporary MP3 file first
                temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_mp3.close()
                tts.save(temp_mp3.name)
                
                # Convert MP3 to WAV if needed (for compatibility)
                # For simplicity, we'll return the MP3 file
                return temp_mp3.name
            
            return temp_file.name
            
        except Exception as e:
            st.error(f"Error saving speech to file: {str(e)}")
            return None
    
    def _play_speech_direct(self, text):
        """Play speech directly without saving to file"""
        try:
            if self.use_pyttsx3:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                # For gTTS, we need to save to file anyway
                audio_file = self._save_speech_to_file(text)
                if audio_file:
                    # Note: Direct playback in Streamlit is limited
                    # The file approach is more reliable
                    pass
                    
        except Exception as e:
            st.error(f"Error playing speech: {str(e)}")
    
    def get_available_voices(self):
        """Get list of available TTS voices"""
        if not self.use_pyttsx3:
            return ["Default (gTTS)"]
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [voice.name for voice in voices] if voices else ["Default"]
        except Exception:
            return ["Default"]
    
    def set_voice(self, voice_index=0):
        """Set the TTS voice by index"""
        if not self.use_pyttsx3:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices and 0 <= voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_index].id)
                return True
        except Exception as e:
            st.error(f"Error setting voice: {str(e)}")
        
        return False
    
    def set_speech_rate(self, rate=150):
        """Set the speech rate (words per minute)"""
        if not self.use_pyttsx3:
            return False
        
        try:
            self.tts_engine.setProperty('rate', max(50, min(400, rate)))
            return True
        except Exception as e:
            st.error(f"Error setting speech rate: {str(e)}")
            return False
    
    def set_volume(self, volume=0.9):
        """Set the speech volume (0.0 to 1.0)"""
        if not self.use_pyttsx3:
            return False
        
        try:
            self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            return True
        except Exception as e:
            st.error(f"Error setting volume: {str(e)}")
            return False
    
    def test_microphone(self):
        """Test microphone functionality"""
        if not self.microphone_available:
            st.warning("Microphone not available in this environment.")
            return False
            
        try:
            with self.microphone as source:
                st.info("Testing microphone... Say something!")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio)
                st.success(f"Microphone test successful! Heard: '{text}'")
                return True
        except Exception as e:
            st.error(f"Microphone test failed: {str(e)}")
            return False
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        # This method can be expanded to track and clean up temporary files
        # For now, we rely on the OS to clean up /tmp files
        pass
