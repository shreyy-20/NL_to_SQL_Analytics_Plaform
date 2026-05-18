"""
Bhashini API wrapper for Text-to-Speech in Hindi and Odia
"""

import asyncio
import aiohttp
import base64
import json
import logging
from typing import Optional, Dict, Any, Tuple

from backend.config import settings

logger = logging.getLogger(__name__)

class BhashiniTTS:
    """Bhashini Text-to-Speech client"""
    
    def __init__(self):
        self.api_key = settings.BHASHINI_API_KEY
        self.api_url = settings.BHASHINI_API_URL
        self.user_id = settings.BHASHINI_USER_ID
        self.language_map = {
            "hi": "hi-IN",
            "or": "or-IN",
            "en": "en-IN"
        }
        self.voice_gender_map = {
            "female": "default_female",
            "male": "default_male"
        }
    
    async def synthesize(
        self,
        text: str,
        language: str = "hi",
        gender: str = "female",
        audio_format: str = "wav"
    ) -> bytes:
        """
        Convert text to speech audio using Bhashini API
        
        Args:
            text: Text to synthesize
            language: Language code (hi, or, en)
            gender: Voice gender (female, male)
            audio_format: Output audio format (wav, mp3)
        
        Returns:
            Audio bytes
        """
        if not self.api_key:
            logger.warning("Bhashini API key not configured, using fallback")
            return self._fallback_tts(text)
        
        try:
            payload = self._build_payload(text, language, gender, audio_format)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": self.api_key,
                    "Content-Type": "application/json",
                    "user-id": self.user_id or ""
                }
                
                async with session.post(
                    f"{self.api_url}/tts/v1/synthesize",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        audio_bytes = self._extract_audio(result)
                        logger.info(f"TTS successful for text: {text[:30]}...")
                        return audio_bytes
                    else:
                        error_text = await response.text()
                        logger.error(f"Bhashini TTS API error: {response.status} - {error_text}")
                        return self._fallback_tts(text)
                        
        except asyncio.TimeoutError:
            logger.error("Bhashini TTS timeout")
            return self._fallback_tts(text)
        except Exception as e:
            logger.error(f"Bhashini TTS exception: {e}")
            return self._fallback_tts(text)
    
    def _build_payload(
        self,
        text: str,
        language: str,
        gender: str,
        audio_format: str
    ) -> Dict:
        """Build API request payload"""
        return {
            "config": {
                "language": {
                    "targetLanguage": self.language_map.get(language, "hi-IN")
                },
                "voice": {
                    "gender": gender,
                    "model": self.voice_gender_map.get(gender, "default_female")
                },
                "audioFormat": audio_format,
                "samplingRate": 16000,
                "speechMarkTypes": []
            },
            "input": [
                {
                    "source": text
                }
            ]
        }
    
    def _extract_audio(self, result: Dict) -> bytes:
        """Extract audio bytes from API response"""
        try:
            # Try different response formats
            if "audio" in result:
                audio_base64 = result["audio"]
            elif "output" in result and len(result["output"]) > 0:
                audio_base64 = result["output"][0].get("audio", "")
            else:
                raise ValueError("No audio in response")
            
            return base64.b64decode(audio_base64)
        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise
    
    def _fallback_tts(self, text: str) -> bytes:
        """Fallback TTS when API fails (return placeholder message)"""
        # In production, you might generate a simple beep or use a local TTS engine
        # For development, return an empty WAV header (simulated)
        import wave
        import io
        
        # Create a simple silent WAV file (8000 Hz, mono, 16-bit)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(8000)
            wav.writeframes(b'\x00\x00' * 8000)  # 1 second of silence
        
        wav_buffer.seek(0)
        return wav_buffer.read()
    
    async def synthesize_batch(
        self,
        texts: list,
        language: str = "hi",
        gender: str = "female"
    ) -> list:
        """Synthesize multiple texts in parallel"""
        tasks = [self.synthesize(text, language, gender) for text in texts]
        return await asyncio.gather(*tasks)

# Singleton instance
_bhashini_tts = None

def get_tts_client() -> BhashiniTTS:
    global _bhashini_tts
    if _bhashini_tts is None:
        _bhashini_tts = BhashiniTTS()
    return _bhashini_tts

# Helper for quick TTS
async def text_to_speech(text: str, language: str = "hi") -> bytes:
    client = get_tts_client()
    return await client.synthesize(text, language)