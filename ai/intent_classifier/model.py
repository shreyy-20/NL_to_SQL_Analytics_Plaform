"""
DistilBERT Intent Classifier Model
Trained on 2000+ agriculture queries in Hindi/Odia/English
"""

import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel
from typing import List, Dict, Any, Optional
import logging
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class IntentClassifier(nn.Module):
    """Neural network for intent classification"""
    
    def __init__(self, num_classes: int = 4, dropout_rate: float = 0.3):
        super(IntentClassifier, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Load DistilBERT base model
        self.bert = DistilBertModel.from_pretrained('distilbert-base-multilingual-cased')
        
        # Classification head
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize classification layer weights"""
        nn.init.xavier_uniform_(self.classifier.weight)
        nn.init.zeros_(self.classifier.bias)
    
    def forward(self, input_ids, attention_mask):
        """
        Forward pass through the network
        
        Args:
            input_ids: Tokenized input IDs
            attention_mask: Attention mask for padding
        
        Returns:
            Logits for each intent class
        """
        # Get BERT outputs
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use CLS token representation
        pooled_output = outputs.last_hidden_state[:, 0, :]
        
        # Apply dropout
        pooled_output = self.dropout(pooled_output)
        
        # Classification
        logits = self.classifier(pooled_output)
        
        return logits

class IntentClassifierModel:
    """Wrapper class for intent classification"""
    
    INTENT_LABELS = ['PAYMENT', 'PRICE', 'SOIL', 'WEATHER']
    INTENT_NAMES = {
        'PAYMENT': {'hi': 'भुगतान', 'or': 'ଭୁଗତାନ', 'en': 'Payment'},
        'PRICE': {'hi': 'मंडी भाव', 'or': 'ମାଣ୍ଡି ଭାବ', 'en': 'Mandi Price'},
        'SOIL': {'hi': 'मिट्टी', 'or': 'ମାଟି', 'en': 'Soil'},
        'WEATHER': {'hi': 'मौसम', 'or': 'ପାଣିପାଗ', 'en': 'Weather'}
    }
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
        
        # Initialize model
        self.model = IntentClassifier(num_classes=len(self.INTENT_LABELS))
        self.model.to(self.device)
        
        # Load pretrained weights if available
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            logger.warning("No pretrained model found, using random initialization")
        
        self.model.eval()
    
    def load_model(self, model_path: str):
        """Load pretrained model weights"""
        try:
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    
    def save_model(self, model_path: str):
        """Save model weights"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        torch.save(self.model.state_dict(), model_path)
        logger.info(f"Model saved to {model_path}")
    
    def predict(self, text: str, language: str = "hi") -> Dict[str, Any]:
        """
        Predict intent for a given text
        
        Args:
            text: Input question text
            language: Language code (hi, or, en)
        
        Returns:
            Dictionary with intent, confidence, and entities
        """
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            logits = self.model(**inputs)
            probabilities = torch.softmax(logits, dim=1)
            predicted_class = torch.argmax(logits, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        intent = self.INTENT_LABELS[predicted_class]
        
        # Extract entities from text
        entities = self._extract_entities(text, intent, language)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "intent_name": self.INTENT_NAMES[intent].get(language, intent),
            "alternative_intents": self._get_alternatives(probabilities[0], predicted_class)
        }
    
    def _extract_entities(self, text: str, intent: str, language: str) -> Dict[str, Any]:
        """Extract relevant entities based on intent"""
        entities = {}
        text_lower = text.lower()
        
        if intent == "PRICE":
            # Extract crop names
            crops = self._extract_crops(text_lower)
            if crops:
                entities["crop"] = crops[0]
            
            # Extract location (market/village)
            locations = self._extract_locations(text_lower)
            if locations:
                entities["location"] = locations[0]
        
        elif intent == "WEATHER":
            # Extract time period
            if any(word in text_lower for word in ["today", "आज", "ଆଜି"]):
                entities["period"] = "today"
            elif any(word in text_lower for word in ["tomorrow", "कल", "କାଲି"]):
                entities["period"] = "tomorrow"
            elif any(word in text_lower for word in ["week", "सप्ताह", "ସପ୍ତାହ"]):
                entities["period"] = "week"
        
        elif intent == "PAYMENT":
            # Extract scheme name
            if "pmkisan" in text_lower or "pm-kisan" in text_lower or "पीएम किसान" in text:
                entities["scheme"] = "pmkisan"
            elif "kalia" in text_lower or "कलिया" in text:
                entities["scheme"] = "kalia"
        
        return entities
    
    def _extract_crops(self, text: str) -> List[str]:
        """Extract crop names from text"""
        known_crops = [
            "धान", "paddy", "rice", "गेहूं", "wheat", "मक्का", "maize",
            "सरसों", "mustard", "आलू", "potato", "टमाटर", "tomato",
            "प्याज", "onion", "सब्जी", "vegetable", "फल", "fruit"
        ]
        return [crop for crop in known_crops if crop.lower() in text]
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location names from text"""
        known_locations = [
            "भुवनेश्वर", "bhubaneswar", "कटक", "cuttack", "पुरी", "puri",
            "बालेश्वर", "balasore", "संबलपुर", "sambalpur", "राउरकेला", "rourkela"
        ]
        return [loc for loc in known_locations if loc.lower() in text]
    
    def _get_alternatives(self, probabilities: torch.Tensor, predicted_idx: int) -> List[Dict[str, float]]:
        """Get alternative intent predictions"""
        alternatives = []
        for idx, prob in enumerate(probabilities):
            if idx != predicted_idx and prob > 0.1:
                alternatives.append({
                    "intent": self.INTENT_LABELS[idx],
                    "confidence": prob.item()
                })
        return sorted(alternatives, key=lambda x: x["confidence"], reverse=True)
    
    def predict_batch(self, texts: List[str], language: str = "hi") -> List[Dict[str, Any]]:
        """Predict intents for multiple texts"""
        return [self.predict(text, language) for text in texts]

# Training function (for reference)
def train_model(train_data_path: str, val_data_path: str, num_epochs: int = 5):
    """Train the intent classifier model"""
    import pandas as pd
    from torch.utils.data import Dataset, DataLoader
    from transformers import AdamW, get_linear_schedule_with_warmup
    
    class QueryDataset(Dataset):
        def __init__(self, texts, labels, tokenizer, max_length=128):
            self.texts = texts
            self.labels = labels
            self.tokenizer = tokenizer
            self.max_length = max_length
        
        def __len__(self):
            return len(self.texts)
        
        def __getitem__(self, idx):
            text = str(self.texts[idx])
            label = self.labels[idx]
            
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors='pt'
            )
            
            return {
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten(),
                'label': torch.tensor(label, dtype=torch.long)
            }
    
    # Load data
    train_df = pd.read_csv(train_data_path)
    val_df = pd.read_csv(val_data_path)
    
    # Initialize model
    model = IntentClassifierModel()
    label_map = {label: idx for idx, label in enumerate(model.INTENT_LABELS)}
    
    train_dataset = QueryDataset(
        train_df['question'].values,
        train_df['intent'].map(label_map).values,
        model.tokenizer
    )
    
    val_dataset = QueryDataset(
        val_df['question'].values,
        val_df['intent'].map(label_map).values,
        model.tokenizer
    )
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    
    # Optimizer
    optimizer = AdamW(model.model.parameters(), lr=2e-5)
    total_steps = len(train_loader) * num_epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
    
    # Training loop
    for epoch in range(num_epochs):
        model.model.train()
        total_loss = 0
        
        for batch in train_loader:
            input_ids = batch['input_ids'].to(model.device)
            attention_mask = batch['attention_mask'].to(model.device)
            labels = batch['label'].to(model.device)
            
            optimizer.zero_grad()
            logits = model.model(input_ids, attention_mask)
            loss = nn.CrossEntropyLoss()(logits, labels)
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        logger.info(f"Epoch {epoch + 1}/{num_epochs}, Loss: {avg_loss:.4f}")
        
        # Validation
        model.model.eval()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(model.device)
                attention_mask = batch['attention_mask'].to(model.device)
                labels = batch['label'].to(model.device)
                
                logits = model.model(input_ids, attention_mask)
                predictions = torch.argmax(logits, dim=1)
                
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        accuracy = correct / total
        logger.info(f"Validation Accuracy: {accuracy:.4f}")
    
    # Save model
    model.save_model("models/distilbert-intent-classifier.pt")
    
    return model