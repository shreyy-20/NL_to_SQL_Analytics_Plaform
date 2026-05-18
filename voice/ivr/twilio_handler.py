"""
Twilio IVR handler for phone calls
Manages call initiation, status tracking, and DTMF input
"""

import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from backend.config import settings

logger = logging.getLogger(__name__)

class TwilioIVRHandler:
    """Twilio-based IVR call handler"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("Twilio not configured, IVR disabled")
    
    async def make_call(
        self,
        to_number: str,
        language: str = "hi",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound IVR call
        
        Args:
            to_number: Recipient phone number (with country code)
            language: Language for the IVR prompt
            custom_message: Custom message to speak
        
        Returns:
            Call information dictionary
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Twilio not configured",
                "call_sid": None,
                "status": "failed"
            }
        
        try:
            # Prepare TwiML URL for the call (should point to your webhook)
            twiml_url = f"{settings.BASE_URL}/api/voice/ivr/welcome"
            if language:
                twiml_url += f"?lang={language}"
            if custom_message:
                twiml_url += f"&msg={custom_message}"
            
            # Make the call
            call = self.client.calls.create(
                url=twiml_url,
                to=to_number,
                from_=self.phone_number,
                status_callback=f"{settings.BASE_URL}/api/voice/call/status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                status_callback_method="POST"
            )
            
            logger.info(f"Call initiated: SID={call.sid}, To={to_number}")
            return {
                "success": True,
                "call_sid": call.sid,
                "status": call.status,
                "to": to_number
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate call: {e}")
            return {
                "success": False,
                "error": str(e),
                "call_sid": None,
                "status": "failed"
            }
    
    def generate_welcome_twiml(self, language: str = "hi", custom_message: str = None) -> str:
        """
        Generate TwiML for welcome message with menu options
        
        Args:
            language: Language code
            custom_message: Custom message to speak first
        
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        # Language-specific prompts
        prompts = {
            "hi": {
                "welcome": "नमस्ते, कृषि क्वेरी में आपका स्वागत है।",
                "menu": "अपनी पीएम किसान या कलिया भुगतान की स्थिति जानने के लिए 1 दबाएं। मंडी भाव जानने के लिए 2 दबाएं। मिट्टी स्वास्थ्य रिपोर्ट के लिए 3 दबाएं। मौसम जानकारी के लिए 4 दबाएं। किसी कर्मचारी से बात करने के लिए 0 दबाएं।",
                "invalid": "क्षमा करें, आपने गलत विकल्प चुना। कृपया पुनः प्रयास करें।",
                "goodbye": "धन्यवाद। कृषि क्वेरी का उपयोग करने के लिए धन्यवाद। शुभकामनाएं।"
            },
            "or": {
                "welcome": "ନମସ୍କାର, କୃଷି କୁଏରୀରେ ଆପଣଙ୍କୁ ସ୍ୱାଗତ।",
                "menu": "ଆପଣଙ୍କ PM-KISAN କିମ୍ବା KALIA ଭୁଗତାନ ସ୍ଥିତି ପାଇଁ 1 ଦାବନ୍ତୁ। ମାଣ୍ଡି ଭାବ ପାଇଁ 2 ଦାବନ୍ତୁ। ମାଟି ସ୍ୱାସ୍ଥ୍ୟ ରିପୋର୍ଟ ପାଇଁ 3 ଦାବନ୍ତୁ। ପାଣିପାଗ ସୂଚନା ପାଇଁ 4 ଦାବନ୍ତୁ।",
                "invalid": "କ୍ଷମା କରନ୍ତୁ, ଆପଣ ଭୁଲ ବିକଳ୍ପ ବାଛିଛନ୍ତି।",
                "goodbye": "ଧନ୍ୟବାଦ। କୃଷି କୁଏରୀ ବ୍ୟବହାର କରିଥିବାରୁ ଧନ୍ୟବାଦ।"
            },
            "en": {
                "welcome": "Welcome to KrishiQuery.",
                "menu": "Press 1 for PM-KISAN or KALIA payment status. Press 2 for mandi prices. Press 3 for soil health report. Press 4 for weather information. Press 0 to speak to an agent.",
                "invalid": "Sorry, invalid option. Please try again.",
                "goodbye": "Thank you for using KrishiQuery. Goodbye."
            }
        }
        
        p = prompts.get(language, prompts["hi"])
        
        if custom_message:
            response.say(custom_message, voice="Polly.Aditi", language="hi-IN")
        else:
            response.say(p["welcome"], voice="Polly.Aditi", language="hi-IN")
            response.say(p["menu"], voice="Polly.Aditi", language="hi-IN")
        
        # Gather DTMF input
        gather = Gather(
            num_digits=1,
            timeout=5,
            action="/api/voice/ivr/menu",
            method="POST"
        )
        gather.say("", voice="Polly.Aditi", language="hi-IN")
        response.append(gather)
        
        # If no input, repeat
        response.redirect("/api/voice/ivr/welcome", method="POST")
        
        return str(response)
    
    def generate_menu_twiml(self, digits: str, language: str = "hi") -> str:
        """
        Generate TwiML based on user's DTMF choice
        
        Args:
            digits: DTMF digits pressed
            language: Language code
        
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        if digits == "1":
            # Payment status - query backend
            response.say("कृपया अपना 10 अंकों का मोबाइल नंबर डायल करें।", voice="Polly.Aditi", language="hi-IN")
            gather = Gather(
                num_digits=10,
                timeout=10,
                action="/api/voice/ivr/payment",
                method="POST"
            )
            gather.say("", voice="Polly.Aditi", language="hi-IN")
            response.append(gather)
        
        elif digits == "2":
            # Mandi price
            response.say("कृपया फसल का नाम बताएं, जैसे धान या गेहूं।", voice="Polly.Aditi", language="hi-IN")
            gather = Gather(
                input="speech dtmf",
                speech_timeout="auto",
                action="/api/voice/ivr/price",
                method="POST"
            )
            gather.say("", voice="Polly.Aditi", language="hi-IN")
            response.append(gather)
        
        elif digits == "3":
            # Soil health
            response.say("कृपया अपना मोबाइल नंबर डायल करें।", voice="Polly.Aditi", language="hi-IN")
            gather = Gather(
                num_digits=10,
                timeout=10,
                action="/api/voice/ivr/soil",
                method="POST"
            )
            gather.say("", voice="Polly.Aditi", language="hi-IN")
            response.append(gather)
        
        elif digits == "4":
            # Weather
            response.say("कृपया अपना गांव या जिला बताएं।", voice="Polly.Aditi", language="hi-IN")
            gather = Gather(
                input="speech dtmf",
                speech_timeout="auto",
                action="/api/voice/ivr/weather",
                method="POST"
            )
            gather.say("", voice="Polly.Aditi", language="hi-IN")
            response.append(gather)
        
        else:
            response.say("क्षमा करें, गलत विकल्प।", voice="Polly.Aditi", language="hi-IN")
            response.redirect("/api/voice/ivr/welcome", method="POST")
        
        return str(response)
    
    def generate_payment_response_twiml(self, payment_info: str, language: str = "hi") -> str:
        """Generate TwiML for payment status response"""
        response = VoiceResponse()
        response.say(payment_info, voice="Polly.Aditi", language="hi-IN")
        response.say("क्या आप कोई और जानकारी चाहेंगे?", voice="Polly.Aditi", language="hi-IN")
        
        gather = Gather(
            num_digits=1,
            timeout=5,
            action="/api/voice/ivr/menu",
            method="POST"
        )
        gather.say("मुख्य मेनू के लिए 1 दबाएं, कॉल समाप्त करने के लिए 9 दबाएं।", voice="Polly.Aditi", language="hi-IN")
        response.append(gather)
        
        return str(response)
    
    def generate_goodbye_twiml(self, language: str = "hi") -> str:
        """Generate goodbye TwiML"""
        response = VoiceResponse()
        prompts = {
            "hi": "धन्यवाद। कृषि क्वेरी का उपयोग करने के लिए धन्यवाद। शुभकामनाएं।",
            "or": "ଧନ୍ୟବାଦ। କୃଷି କୁଏରୀ ବ୍ୟବହାର କରିଥିବାରୁ ଧନ୍ୟବାଦ।",
            "en": "Thank you for using KrishiQuery. Goodbye."
        }
        response.say(prompts.get(language, prompts["hi"]), voice="Polly.Aditi", language="hi-IN")
        response.hangup()
        return str(response)
    
    async def get_call_status(self, call_sid: str) -> str:
        """Get status of a call by SID"""
        if not self.enabled:
            return "unknown"
        
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status
        except Exception as e:
            logger.error(f"Failed to get call status: {e}")
            return "unknown"

# Global instance
_twilio_handler = None

def get_ivr_handler() -> TwilioIVRHandler:
    global _twilio_handler
    if _twilio_handler is None:
        _twilio_handler = TwilioIVRHandler()
    return _twilio_handler