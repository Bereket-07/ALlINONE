import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import ELEVEN_LABS_API_KEY, ELEVEN_LABS_BASE_URL

class ElevenLabsService:
    """Service for Eleven Labs text-to-speech"""
    
    def __init__(self):
        self.api_key = ELEVEN_LABS_API_KEY
        self.base_url = ELEVEN_LABS_BASE_URL
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def text_to_speech(self, text: str, 
                           voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                           model_id: str = "eleven_monolingual_v1",
                           voice_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert text to speech using Eleven Labs"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            payload = {
                "text": text,
                "model_id": model_id
            }
            
            if voice_settings:
                payload["voice_settings"] = voice_settings
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        return {
                            "audio_data": audio_data,
                            "format": "mp3",
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"TTS failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Text-to-speech error: {str(e)}"}
    
    async def get_voices(self) -> Dict[str, Any]:
        """Get available voices"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/voices"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "voices": result.get("voices", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get voices: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get voices error: {str(e)}"}
    
    async def get_voice_settings(self, voice_id: str) -> Dict[str, Any]:
        """Get voice settings for a specific voice"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/voices/{voice_id}/settings/edit"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "settings": result,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get voice settings: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get voice settings error: {str(e)}"}
    
    async def clone_voice(self, name: str, description: str, audio_files: List[bytes]) -> Dict[str, Any]:
        """Clone a voice from audio samples"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/voices/add"
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('name', name)
            data.add_field('description', description)
            
            for i, audio_file in enumerate(audio_files):
                data.add_field(f'files', audio_file, 
                             filename=f'audio_{i}.mp3',
                             content_type='audio/mpeg')
            
            headers = {"xi-api-key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "voice_id": result.get("voice_id"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Voice cloning failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Voice cloning error: {str(e)}"}
    
    async def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        """Delete a voice"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/voices/{voice_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "Voice deleted"}
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to delete voice: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Delete voice error: {str(e)}"}
    
    async def stream_text_to_speech(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Stream text-to-speech for real-time playback"""
        try:
            if not self.api_key:
                return {"error": "Eleven Labs API key not configured"}
            
            url = f"{self.base_url}/text-to-speech/{voice_id}/stream"
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        # Return streaming response
                        return {
                            "stream": response.content,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Streaming TTS failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Streaming TTS error: {str(e)}"} 