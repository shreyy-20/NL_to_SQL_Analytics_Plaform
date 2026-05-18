"""
Intent prediction utility for production use
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Global model instance
_model_instance = None

class IntentPredictor:
    """Singleton predictor for intent classification"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path or "models/distilbert-intent-classifier.pt"
        self._load_model()
    
    def _load_model(self):
        """Load the intent classification model"""
        try:
            from ai.intent_classifier.model import IntentClassifierModel
            
            if Path(self.model_path).exists():
                self.model = IntentClassifierModel(model_path=self.model_path)
                logger.info("Intent classifier model loaded successfully")
            else:
                logger.warning(f"Model not found at {self.model_path}, using rule-based fallback")
                self.model = None
        except Exception as e:
            logger.error(f"Failed to load intent model: {e}")
            self.model = None
    
    def predict(self, text: str, language: str = "hi") -> Dict[str, Any]:
        """
        Predict intent for a given text
        
        Args:
            text: Input question text
            language: Language code (hi, or, en)
        
        Returns:
            Intent prediction with confidence and entities
        """
        if self.model is None:
            # Fallback to rule-based prediction
            return self._rule_based_predict(text, language)
        
        try:
            return self.model.predict(text, language)
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_predict(text, language)
    
    def _rule_based_predict(self, text: str, language: str) -> Dict[str, Any]:
        """Simple rule-based fallback for intent prediction"""
        text_lower = text.lower()
        
        # Payment-related keywords
        payment_keywords = [
            "pmkisan", "pm-kisan", "kalia", "किश्त", "भुगतान", "पैसा",
            "payment", "installment", "पीएम किसान", "कलिया"
        ]
        if any(kw in text_lower for kw in payment_keywords):
            return {
                "intent": "PAYMENT",
                "confidence": 0.7,
                "entities": self._extract_entities_simple(text, "PAYMENT"),
                "intent_name": "भुगतान"
            }
        
        # Price-related keywords
        price_keywords = [
            "भाव", "मंडी", "दाम", "कीमत", "price", "mandi", "rate",
            "कितने का", "कितना दाम"
        ]
        if any(kw in text_lower for kw in price_keywords):
            return {
                "intent": "PRICE",
                "confidence": 0.7,
                "entities": self._extract_entities_simple(text, "PRICE"),
                "intent_name": "मंडी भाव"
            }
        
        # Soil-related keywords
        soil_keywords = [
            "मिट्टी", "soil", "खाद", "उर्वरक", "fertilizer",
            "नाइट्रोजन", "phosphorus", "potassium", "पीएच"
        ]
        if any(kw in text_lower for kw in soil_keywords):
            return {
                "intent": "SOIL",
                "confidence": 0.7,
                "entities": self._extract_entities_simple(text, "SOIL"),
                "intent_name": "मिट्टी स्वास्थ्य"
            }
        
        # Weather-related keywords
        weather_keywords = [
            "मौसम", "बारिश", "तापमान", "weather", "rain", "temperature",
            "गर्मी", "ठंड", "बादल"
        ]
        if any(kw in text_lower for kw in weather_keywords):
            return {
                "intent": "WEATHER",
                "confidence": 0.7,
                "entities": self._extract_entities_simple(text, "WEATHER"),
                "intent_name": "मौसम"
            }
        
        # Unknown intent
        return {
            "intent": "UNKNOWN",
            "confidence": 0.3,
            "entities": {},
            "intent_name": "अज्ञात"
        }
    
    def _extract_entities_simple(self, text: str, intent: str) -> Dict[str, Any]:
        """Simple entity extraction for fallback"""
        entities = {}
        text_lower = text.lower()
        
        if intent == "PRICE":
            # Try to extract crop
            crops = ["धान", "गेहूं", "मक्का", "सरसों", "आलू", "टमाटर", "प्याज"]
            for crop in crops:
                if crop in text:
                    entities["crop"] = crop
                    break
            
            # Try to extract location
            locations = ["भुवनेश्वर", "कटक", "पुरी", "बालेश्वर", "संबलपुर"]
            for loc in locations:
                if loc in text:
                    entities["location"] = loc
                    break
        
        elif intent == "PAYMENT":
            if "pm" in text_lower or "किसान" in text:
                entities["scheme"] = "pmkisan"
            elif "kalia" in text_lower or "कलिया" in text:
                entities["scheme"] = "kalia"
        
        elif intent == "WEATHER":
            if "आज" in text or "today" in text_lower:
                entities["period"] = "today"
            elif "कल" in text or "tomorrow" in text_lower:
                entities["period"] = "tomorrow"
            elif "सप्ताह" in text or "week" in text_lower:
                entities["period"] = "week"
        
        return entities

# Singleton instance for fast access
_predictor_instance = None

def get_predictor() -> IntentPredictor:
    """Get singleton predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = IntentPredictor()
    return _predictor_instance

def predict_intent(text: str, language: str = "hi") -> Dict[str, Any]:
    """
    Convenience function for intent prediction
    
    Args:
        text: Input question text
        language: Language code
    
    Returns:
        Intent prediction result
    """
    predictor = get_predictor()
    return predictor.predict(text, language)

def is_model_loaded() -> bool:
    """Check if model is loaded"""
    global _predictor_instance
    return _predictor_instance is not None and _predictor_instance.model is not None

def load_intent_model(model_path: Optional[str] = None):
    """Force load the intent model"""
    global _predictor_instance
    _predictor_instance = IntentPredictor(model_path)
