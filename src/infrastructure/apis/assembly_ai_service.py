import assemblyai as aai
import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any, List
from src.config import ASSEMBLY_AI_API_KEY, ASSEMBLY_AI_BASE_URL

class AssemblyAIService:
    """Service for Assembly AI speech-to-text and audio processing"""
    
    def __init__(self):
        self.api_key = ASSEMBLY_AI_API_KEY
        self.base_url = ASSEMBLY_AI_BASE_URL
        if self.api_key:
            aai.settings.api_key = self.api_key
            self.transcriber = aai.Transcriber()
    
    async def transcribe_audio(self, audio_file_path: str, language_code: str = "en") -> Dict[str, Any]:
        """Transcribe audio file to text"""
        try:
            if not self.api_key:
                return {"error": "Assembly AI API key not configured"}
            
            # Configure transcription
            config = aai.TranscriptionConfig(
                language_code=language_code,
                speaker_labels=True,
                auto_highlights=True,
                entity_detection=True
            )
            
            # Transcribe the audio
            transcript = await asyncio.to_thread(
                self.transcriber.transcribe,
                audio_file_path,
                config=config
            )
            
            if transcript.status == aai.TranscriptStatus.error:
                return {"error": f"Transcription failed: {transcript.error}"}
            
            return {
                "text": transcript.text,
                "confidence": transcript.confidence,
                "speakers": transcript.speakers,
                "highlights": transcript.highlights,
                "entities": transcript.entities,
                "utterances": [
                    {
                        "speaker": u.speaker,
                        "text": u.text,
                        "start": u.start,
                        "end": u.end
                    } for u in transcript.utterances
                ]
            }
            
        except Exception as e:
            return {"error": f"Transcription error: {str(e)}"}
    
    async def real_time_transcription(self, audio_stream) -> Dict[str, Any]:
        """Real-time transcription from audio stream"""
        try:
            if not self.api_key:
                return {"error": "Assembly AI API key not configured"}
            
            # Configure real-time transcription
            config = aai.RealtimeTranscriptionConfig(
                sample_rate=16000,
                language_code="en"
            )
            
            # Create real-time transcriber
            transcriber = aai.RealtimeTranscriber(
                config=config,
                on_data=self._on_data,
                on_error=self._on_error,
                on_open=self._on_open,
                on_close=self._on_close
            )
            
            # Start transcription
            transcriber.connect()
            
            # Stream audio data
            for chunk in audio_stream:
                transcriber.stream(chunk)
            
            transcriber.disconnect()
            
            return {"status": "completed"}
            
        except Exception as e:
            return {"error": f"Real-time transcription error: {str(e)}"}
    
    def _on_data(self, transcript: aai.RealtimeTranscript):
        """Handle real-time transcript data"""
        if transcript.text:
            print(f"Real-time: {transcript.text}")
    
    def _on_error(self, error: aai.RealtimeError):
        """Handle real-time transcription errors"""
        print(f"Real-time error: {error}")
    
    def _on_open(self, session_id: str):
        """Handle real-time session open"""
        print(f"Real-time session opened: {session_id}")
    
    def _on_close(self, session_id: str):
        """Handle real-time session close"""
        print(f"Real-time session closed: {session_id}")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of transcribed text"""
        try:
            if not self.api_key:
                return {"error": "Assembly AI API key not configured"}
            
            # Use Assembly AI's sentiment analysis
            config = aai.TranscriptionConfig(
                sentiment_analysis=True
            )
            
            # This would typically be done on transcribed text
            # For now, we'll return a placeholder
            return {
                "sentiment": "positive",
                "confidence": 0.85,
                "text": text
            }
            
        except Exception as e:
            return {"error": f"Sentiment analysis error: {str(e)}"} 