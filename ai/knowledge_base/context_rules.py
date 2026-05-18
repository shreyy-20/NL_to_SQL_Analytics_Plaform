"""
Context-aware term resolution for ambiguous words
Handles words like "high", "low", "good", "bad" based on context
"""

import re
from typing import Dict, Any, List, Tuple, Optional
import json
from pathlib import Path

class ContextRules:
    """Resolve ambiguous terms based on domain context"""
    
    def __init__(self):
        self.terms_json = self._load_terms()
        self._init_rule_map()
    
    def _load_terms(self) -> Dict:
        """Load terms from JSON file"""
        terms_path = Path(__file__).parent / "terms.json"
        try:
            with open(terms_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"terms": {}}
    
    def _init_rule_map(self):
        """Initialize context-specific rule mappings"""
        
        self.thresholds = {
            "soil": {
                "nitrogen": {"low": 0, "medium": 280, "high": 500},
                "phosphorus": {"low": 0, "medium": 25, "high": 50},
                "potassium": {"low": 0, "medium": 120, "high": 300},
                "ph": {"very_acidic": 0, "acidic": 6, "neutral": 6.5, "alkaline": 7.5}
            },
            "price": {
                "paddy": {"very_low": 1500, "low": 1800, "average": 2000, "high": 2200, "very_high": 2500},
                "wheat": {"low": 2000, "average": 2250, "high": 2500},
                "maize": {"low": 1800, "average": 2000, "high": 2200}
            }
        }
        
        self.synonyms = {
            "high": ["high", "good", "excellent", "great", "better", "higher", "ऊंचा", "अच्छा", "बेहतर"],
            "low": ["low", "poor", "bad", "less", "lower", "निम्न", "खराब", "कम"],
            "check": ["check", "see", "view", "show", "tell", "देखें", "बताएं", "चेक करें"],
            "status": ["status", "update", "info", "information", "स्थिति", "जानकारी"]
        }
    
    def resolve_ambiguous_term(
        self, 
        term: str, 
        context: str, 
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Resolve ambiguous term based on domain context
        
        Args:
            term: The ambiguous word (e.g., "high", "low")
            context: Domain context (payment, price, soil, weather)
            language: Language code
        
        Returns:
            Resolved meaning with threshold values
        """
        term_lower = term.lower()
        
        # Map to standard term
        standard_term = self._map_to_standard(term_lower)
        
        if context == "soil":
            return self._resolve_soil_ambiguity(standard_term)
        elif context == "price":
            return self._resolve_price_ambiguity(standard_term)
        elif context == "payment":
            return self._resolve_payment_ambiguity(standard_term)
        elif context == "weather":
            return self._resolve_weather_ambiguity(standard_term)
        else:
            return {"value": standard_term, "confidence": 0.5}
    
    def _map_to_standard(self, term: str) -> str:
        """Map synonyms to standard terms"""
        for standard, synonyms in self.synonyms.items():
            if term in synonyms or any(term in syn for syn in synonyms):
                return standard
        return term
    
    def _resolve_soil_ambiguity(self, term: str) -> Dict[str, Any]:
        """Resolve ambiguous terms in soil context"""
        result = {"original_term": term, "context": "soil"}
        
        if term in ["high", "low"]:
            result["type"] = "comparative"
            result["interpretations"] = {
                "nitrogen": {
                    "high": f"> {self.thresholds['soil']['nitrogen']['high']} kg/ha",
                    "low": f"< {self.thresholds['soil']['nitrogen']['medium']} kg/ha"
                },
                "phosphorus": {
                    "high": f"> {self.thresholds['soil']['phosphorus']['high']} kg/ha",
                    "low": f"< {self.thresholds['soil']['phosphorus']['medium']} kg/ha"
                },
                "potassium": {
                    "high": f"> {self.thresholds['soil']['potassium']['high']} kg/ha",
                    "low": f"< {self.thresholds['soil']['potassium']['medium']} kg/ha"
                }
            }
            result["query_suggestion"] = f"Check if any soil parameter is {term}"
        
        elif term == "acidic":
            result["type"] = "property"
            result["value"] = f"pH < {self.thresholds['soil']['ph']['acidic']}"
            result["recommendation"] = "Consider adding lime to neutralize soil"
        
        elif term == "alkaline":
            result["type"] = "property"  
            result["value"] = f"pH > {self.thresholds['soil']['ph']['alkaline']}"
            result["recommendation"] = "Consider adding organic matter or gypsum"
        
        return result
    
    def _resolve_price_ambiguity(self, term: str) -> Dict[str, Any]:
        """Resolve ambiguous terms in price context"""
        result = {"original_term": term, "context": "price"}
        
        if term in ["high", "low", "good", "bad"]:
            result["type"] = "comparative"
            result["interpretations"] = {}
            
            for crop, thresholds in self.thresholds["price"].items():
                if term in ["high", "good"]:
                    result["interpretations"][crop] = f"> ₹{thresholds['average']}/quintal"
                else:
                    result["interpretations"][crop] = f"< ₹{thresholds['average']}/quintal"
        
        return result
    
    def _resolve_payment_ambiguity(self, term: str) -> Dict[str, Any]:
        """Resolve ambiguous terms in payment context"""
        result = {"original_term": term, "context": "payment"}
        
        if term in ["pending", "delayed", "late"]:
            result["type"] = "status"
            result["query"] = "SELECT status FROM payments WHERE status IN ('pending', 'processing')"
            result["suggestion"] = "Check for pending or delayed payments"
        
        elif term in ["received", "credited", "completed"]:
            result["type"] = "status"
            result["query"] = "SELECT status FROM payments WHERE status = 'completed'"
        
        return result
    
    def _resolve_weather_ambiguity(self, term: str) -> Dict[str, Any]:
        """Resolve ambiguous terms in weather context"""
        result = {"original_term": term, "context": "weather"}
        
        if term in ["hot", "high", "warm"]:
            result["type"] = "temperature"
            result["comparison"] = "above normal"
        elif term in ["cold", "low", "cool"]:
            result["type"] = "temperature"
            result["comparison"] = "below normal"
        elif term in ["rain", "rainy", "wet"]:
            result["type"] = "precipitation"
            result["query"] = "SELECT rainfall FROM weather WHERE rainfall > 0"
        
        return result
    
    def extract_numerical_threshold(
        self, 
        phrase: str, 
        context: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Extract numerical thresholds from phrases like "more than 2000"
        
        Returns:
            Tuple of (operator, value, unit) or None
        """
        patterns = [
            (r'(?:more than|above|greater than|>)\s*(\d+(?:\.\d+)?)', '>'),
            (r'(?:less than|below|under|<)\s*(\d+(?:\.\d+)?)', '<'),
            (r'(?:between|within)\s*(\d+(?:\.\d+)?)\s*(?:and|to)\s*(\d+(?:\.\d+)?)', 'between')
        ]
        
        for pattern, operator in patterns:
            match = re.search(pattern, phrase, re.IGNORECASE)
            if match:
                if operator == 'between':
                    return ('between', float(match.group(1)), float(match.group(2)))
                else:
                    return (operator, float(match.group(1)), '')
        
        return None
    
    def get_context_specific_sql(
        self, 
        ambiguous_term: str, 
        base_query: str, 
        context: str
    ) -> str:
        """Generate context-specific SQL for ambiguous terms"""
        resolved = self.resolve_ambiguous_term(ambiguous_term, context)
        
        if resolved.get("type") == "comparative":
            # Add appropriate WHERE clauses based on context
            if context == "soil":
                return base_query + " WHERE nitrogen > 280 OR phosphorus > 25 OR potassium > 120"
            elif context == "price":
                return base_query + " WHERE price > 2000"
        
        return base_query

# Global instance
context_rules = ContextRules()

def resolve_term(term: str, context: str, language: str = "hi") -> Dict[str, Any]:
    """Convenience function for term resolution"""
    return context_rules.resolve_ambiguous_term(term, context, language)

def extract_threshold(phrase: str, context: str) -> Optional[Tuple[str, float, str]]:
    """Extract numerical thresholds from phrases"""
    return context_rules.extract_numerical_threshold(phrase, context)