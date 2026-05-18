"""
Voice API endpoints for speech-to-text and text-to-speech
Integrates with Bhashini API for Hindi/Odia support
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional
from pydantic import BaseModel
import logging
import io
import base64
import tempfile
import os

from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class STTRequest(BaseModel):
    """Speech-to-text request model"""
    audio_base64: str
    language: str = "hi"  # hi, or, en
    audio_format: str = "wav"

class TTSRequest(BaseModel):
    """Text-to-speech request model"""
    text: str
    language: str = "hi"
    gender: str = "female"

class VoiceCallRequest(BaseModel):
    """IVR call request model"""
    phone_number: str
    language: str = "hi"
    message: Optional[str] = None

@router.post("/stt")
async def speech_to_text(
    request: STTRequest
):
    """
    Convert speech audio to text using Bhashini API
    """
    if not settings.ENABLE_VOICE:
        raise HTTPException(status_code=503, detail="Voice services are currently disabled")
    
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio_base64)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{request.audio_format}", delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            # Call Bhashini STT API
            from voice.stt.bhashini_stt import BhashiniSTT
            stt_client = BhashiniSTT()
            text = await stt_client.transcribe(tmp_path, request.language)
            
            return {
                "success": True,
                "text": text,
                "language": request.language
            }
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"STT error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")

@router.post("/tts")
async def text_to_speech(
    request: TTSRequest
):
    """
    Convert text to speech audio using Bhashini API
    """
    if not settings.ENABLE_VOICE:
        raise HTTPException(status_code=503, detail="Voice services are currently disabled")
    
    try:
        # Call Bhashini TTS API
        from voice.tts.bhashini_tts import BhashiniTTS
        tts_client = BhashiniTTS()
        audio_data = await tts_client.synthesize(
            text=request.text,
            language=request.language,
            gender=request.gender
        )
        
        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.post("/stt/upload")
async def speech_to_text_upload(
    audio_file: UploadFile = File(...),
    language: str = Form("hi")
):
    """
    Upload audio file for speech recognition
    """
    if not settings.ENABLE_VOICE:
        raise HTTPException(status_code=503, detail="Voice services are currently disabled")
    
    try:
        # Read uploaded file
        audio_data = await audio_file.read()
        
        # Save to temporary file
        file_extension = audio_file.filename.split('.')[-1]
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name
        
        try:
            # Call Bhashini STT API
            from voice.stt.bhashini_stt import BhashiniSTT
            stt_client = BhashiniSTT()
            text = await stt_client.transcribe(tmp_path, language)
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "filename": audio_file.filename
            }
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"STT upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")

@router.post("/call")
async def initiate_ivr_call(
    request: VoiceCallRequest
):
    """
    Initiate an IVR call to a farmer using Twilio
    """
    if not settings.ENABLE_IVR:
        raise HTTPException(status_code=503, detail="IVR services are currently disabled")
    
    if not settings.TWILIO_ACCOUNT_SID:
        raise HTTPException(status_code=503, detail="Twilio not configured")
    
    try:
        from voice.ivr.twilio_handler import TwilioIVRHandler
        ivr_handler = TwilioIVRHandler()
        
        call_info = await ivr_handler.make_call(
            to_number=request.phone_number,
            language=request.language,
            custom_message=request.message
        )
        
        return {
            "success": True,
            "call_sid": call_info["call_sid"],
            "status": call_info["status"],
            "message": "Call initiated successfully"
        }
        
    except Exception as e:
        logger.error(f"IVR call error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Call initiation failed: {str(e)}")

@router.post("/call/status")
async def call_status_webhook(
    CallSid: str,
    CallStatus: str,
    **kwargs
):
    """
    Twilio webhook for call status updates
    """
    logger.info(f"Call {CallSid} status: {CallStatus}")
    # Store call status in database or cache
    return {"status": "received"}

@router.get("/call/{call_sid}/status")
async def get_call_status(
    call_sid: str
):
    """
    Get status of an IVR call
    """
    try:
        from voice.ivr.twilio_handler import TwilioIVRHandler
        ivr_handler = TwilioIVRHandler()
        status = await ivr_handler.get_call_status(call_sid)
        
        return {
            "call_sid": call_sid,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting call status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for voice services
    """
    return {
        "languages": [
            {"code": "hi", "name": "Hindi", "name_native": "हिन्दी"},
            {"code": "or", "name": "Odia", "name_native": "ଓଡ଼ିଆ"},
            {"code": "en", "name": "English", "name_native": "English"}
        ],
        "default": "hi",
        "tts_voices": {
            "hi": ["female", "male"],
            "or": ["female", "male"],
            "en": ["female", "male"]
        }
    }

@router.get("/test")
async def test_voice_services():
    """
    Test endpoint to verify voice services are working
    """
    results = {
        "stt": {"status": "unknown", "message": ""},
        "tts": {"status": "unknown", "message": ""}
    }
    
    # Test STT with a small test file if available
    # This is a placeholder - actual implementation would test API connectivity
    
    # Test TTS
    try:
        from voice.tts.bhashini_tts import BhashiniTTS
        tts_client = BhashiniTTS()
        # Small test
        results["tts"]["status"] = "configured"
        results["tts"]["message"] = "Bhashini API key found"
    except Exception as e:
        results["tts"]["status"] = "error"
        results["tts"]["message"] = str(e)
    
    return results