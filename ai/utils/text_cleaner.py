"""
Text cleaning utilities for Indian languages
Handles normalization, transliteration, and cleaning
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Optional

# Mapping for common misspellings and variations
COMMON_MAPPINGS = {
    # Hindi variations
    'किसान': ['kisan', 'kisaan', 'kishan'],
    'भुगतान': ['bhugtan', 'bhugataan', 'payment'],
    'मंडी': ['mandi', 'mandee', 'mandy'],
    'धान': ['dhan', 'dhaan', 'paddy', 'rice'],
    
    # Odia variations  
    'କୃଷକ': ['krushak', 'krusak', 'krisak'],
    'ଭୁଗତାନ': ['bhugatan', 'bhugataan', 'payment'],
    'ମାଣ୍ଡି': ['mandi', 'mandee', 'mandy'],
    'ଧାନ': ['dhan', 'dhaan', 'paddy'],
    
    # Scheme names
    'pmkisan': ['pm kisan', 'pm-kisan', 'पीएम किसान', 'pmkisaan'],
    'kalia': ['kaliya', 'कलिया', 'କଳିଆ', 'kaleea'],
}

# Stop words in Hindi and Odia
STOP_WORDS = {
    'hi': ['और', 'से', 'को', 'का', 'की', 'के', 'ने', 'पर', 'में', 'है', 'था', 'थी', 'थे'],
    'or': ['ଏବଂ', 'ରୁ', 'କୁ', 'ର', 'ରେ', 'ଥିଲା', 'ଅଛି'],
    'en': ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
}

def clean_text(
    text: str,
    language: str = "hi",
    remove_stopwords: bool = False,
    normalize_unicode: bool = True
) -> str:
    """
    Clean and normalize text for processing
    
    Args:
        text: Input text string
        language: Language code (hi, or, en)
        remove_stopwords: Whether to remove stop words
        normalize_unicode: Whether to normalize Unicode characters
    
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Normalize unicode
    if normalize_unicode:
        text = unicodedata.normalize('NFKC', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation (keep Indic script punctuation)
    text = re.sub(r'[^\w\s\u0900-\u097F\u0B00-\u0B7F]', ' ', text)
    
    # Fix common mappings
    for standard, variations in COMMON_MAPPINGS.items():
        for var in variations:
            if var in text:
                text = text.replace(var, standard)
    
    # Remove stop words if requested
    if remove_stopwords and language in STOP_WORDS:
        words = text.split()
        words = [w for w in words if w not in STOP_WORDS[language]]
        text = ' '.join(words)
    
    # Remove extra whitespace again
    text = ' '.join(text.split())
    
    return text.strip()

def normalize_indian_text(text: str, target_language: str = "hi") -> str:
    """
    Normalize Indian language text with common spelling variations
    
    Args:
        text: Input text
        target_language: Target language for normalization
    
    Returns:
        Normalized text
    """
    # Convert numbers to words for better matching
    number_map = {
        '0': 'शून्य', '1': 'एक', '2': 'दो', '3': 'तीन', '4': 'चार',
        '5': 'पांच', '6': 'छह', '7': 'सात', '8': 'आठ', '9': 'नौ'
    }
    
    for digit, word in number_map.items():
        text = text.replace(digit, word)
    
    # Handle currency amounts
    text = re.sub(r'(\d+)\s*रुपए', r'\1 रुपये', text)
    text = re.sub(r'(\d+)\s*रु', r'\1 रुपये', text)
    
    return text

def extract_entities(text: str, entity_types: List[str] = None) -> Dict[str, List[str]]:
    """
    Extract entities from text using patterns
    
    Args:
        text: Input text
        entity_types: Types of entities to extract
    
    Returns:
        Dictionary of extracted entities
    """
    if entity_types is None:
        entity_types = ['crops', 'amounts', 'dates', 'locations']
    
    entities = {}
    
    # Extract crop names
    if 'crops' in entity_types:
        crops = []
        crop_list = ['धान', 'गेहूं', 'मक्का', 'सरसों', 'आलू', 'टमाटर', 'प्याज']
        for crop in crop_list:
            if crop in text:
                crops.append(crop)
        entities['crops'] = crops
    
    # Extract amounts/numbers
    if 'amounts' in entity_types:
        amounts = re.findall(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:रुपए|रु|₹)?', text)
        entities['amounts'] = [float(a.replace(',', '')) for a in amounts]
    
    # Extract dates
    if 'dates' in entity_types:
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD/MM/YYYY
            r'(\d{1,2}\s+(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर)\s+\d{2,4})',
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        entities['dates'] = dates
    
    # Extract locations
    if 'locations' in entity_types:
        locations = []
        location_list = [
            'भुवनेश्वर', 'कटक', 'पुरी', 'बालेश्वर', 'संबलपुर',
            'राउरकेला', 'बरहमपुर', 'झारसुगुड़ा'
        ]
        for loc in location_list:
            if loc in text:
                locations.append(loc)
        entities['locations'] = locations
    
    return entities

def detect_language(text: str) -> str:
    """
    Detect language of input text (simplified)
    
    Returns:
        Language code: 'hi', 'or', 'en'
    """
    # Check for Devanagari script (Hindi, Marathi, etc.)
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    
    # Check for Odia script
    if re.search(r'[\u0B00-\u0B7F]', text):
        return 'or'
    
    # Default to English
    return 'en'

def chunk_text(text: str, max_length: int = 512) -> List[str]:
    """
    Split text into chunks for model processing
    
    Args:
        text: Input text
        max_length: Maximum chunk length
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def remove_noise(text: str) -> str:
    """
    Remove noise from text (emojis, special characters, etc.)
    """
    # Remove emojis
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub(r'', text)
    
    # Remove extra spaces and special characters
    text = re.sub(r'[^\w\s\u0900-\u097F\u0B00-\u0B7F]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()