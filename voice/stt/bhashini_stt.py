"""
Bhashini API wrapper for Speech-to-Text in Hindi and Odia
"""

import asyncio
import aiohttp
import base64
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from backend.config import settings

logger = logging.getLogger(__name__)

class BhashiniSTT:
    """Bhashini Speech-to-Text client"""
    
    def __init__(self):
        self.api_key = settings.BHASHINI_API_KEY
        self.api_url = settings.BHASHINI_API_URL
        self.user_id = settings.BHASHINI_USER_ID
        self.language_map = {
            "hi": "hi-IN",  # Hindi (India)
            "or": "or-IN",  # Odia
            "en": "en-IN"   # English (Indian)
        }
    
    async def transcribe(
        self,
        audio_file_path: str,
        language: str = "hi",
        audio_format: str = "wav"
    ) -> str:
        """
        Convert speech audio to text using Bhashini API
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (hi, or, en)
            audio_format: Audio format (wav, mp3, etc.)
        
        Returns:
            Transcribed text string
        """
        if not self.api_key:
            logger.warning("Bhashini API key not configured, using fallback")
            return self._fallback_stt()
        
        try:
            # Read audio file and encode as base64
            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            
            # Prepare API request
            payload = self._build_payload(audio_base64, language, audio_format)
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                    "user-id": self.user_id or ""
                }
                
                async with session.post(
                    f"{self.api_url}/stt/v1/transcribe",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        text = self._extract_text(result)
                        logger.info(f"STT successful: {text[:50]}...")
                        return text
                    else:
                        error_text = await response.text()
                        logger.error(f"Bhashini STT API error: {response.status} - {error_text}")
                        return self._fallback_stt()
                        
        except asyncio.TimeoutError:
            logger.error("Bhashini STT timeout")
            return self._fallback_stt()
        except Exception as e:
            logger.error(f"Bhashini STT exception: {e}")
            return self._fallback_stt()
    
    def _build_payload(self, audio_base64: str, language: str, audio_format: str) -> Dict:
        """Build API request payload"""
        return {
            "config": {
                "language": {
                    "sourceLanguage": self.language_map.get(language, "hi-IN")
                },
                "transcriptionFormat": {
                    "value": "text"
                },
                "audioFormat": audio_format,
                "samplingRate": 16000,
                "postProcess": {
                    "value": True
                }
            },
            "audio": [
                {
                    "audioContent": audio_base64
                }
            ]
        }
    
    def _extract_text(self, result: Dict) -> str:
        """Extract transcribed text from API response"""
        try:
            # Try different response formats
            if "output" in result:
                return result["output"][0]["source"]
            elif "transcript" in result:
                return result["transcript"]
            elif "text" in result:
                return result["text"]
            else:
                return str(result)
        except Exception:
            return "Sorry, could not transcribe audio."
    
    def _fallback_stt(self) -> str:
        """Fallback STT when API fails (mock for development)"""
        return "मेरी PM-KISAN की किश्त आई क्या?"
    
    async def transcribe_stream(self, audio_stream: bytes, language: str = "hi") -> str:
        """Transcribe streaming audio data"""
        # Similar to transcribe but accepts bytes directly
        audio_base64 = base64.b64encode(audio_stream).decode("utf-8")
        payload = self._build_payload(audio_base64, language, "wav")
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": self.api_key, "Content-Type": "application/json"}
            async with session.post(
                f"{self.api_url}/stt/v1/transcribe",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._extract_text(result)
                return self._fallback_stt()

# Singleton instance
_bhashini_stt = None

def get_stt_client() -> BhashiniSTT:
    global _bhashini_stt
    if _bhashini_stt is None:
        _bhashini_stt = BhashiniSTT()
    return _bhashini_stt