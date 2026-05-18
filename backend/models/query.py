"""
Query related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Natural language query request model"""
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question from farmer"
    )
    phone_number: str = Field(
        ...,
        pattern=r'^[6-9]\d{9}$',
        description="Farmer's 10-digit mobile number"
    )
    language: str = Field(
        default="hi",
        pattern='^(hi|or|en)$',
        description="Language code: hi (Hindi), or (Odia), en (English)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for query processing"
    )
    
    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "मेरी PM-KISAN की किश्त आई क्या?",
                "phone_number": "9876543210",
                "language": "hi"
            }
        }

class QueryResult(BaseModel):
    """Internal query result model"""
    answer: str
    data: Optional[Any] = None
    intent: str
    confidence: float
    query_executed: Optional[str] = None
    processing_time_ms: int
    success: bool = True
    error: Optional[str] = None

class QueryResponse(BaseModel):
    """API response model for queries"""
    success: bool
    answer: str
    data: Optional[Any] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None
    query_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "हाँ, आपकी PM-KISAN की तीसरी किश्त ₹2000 दिनांक 15-11-2023 को जारी हुई है।",
                "intent": "PAYMENT",
                "confidence": 0.95,
                "processing_time_ms": 1234,
                "query_id": "abc123"
            }
        }

class QueryHistoryResponse(BaseModel):
    """Query history response model"""
    queries: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int

class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: str
    confidence: float
    entities: Dict[str, Any] = Field(default_factory=dict)
    alternative_intents: List[Dict[str, float]] = Field(default_factory=list)

class SQLGenerationRequest(BaseModel):
    """Request for SQL generation"""
    question: str
    intent: str
    entities: Dict[str, Any]
    farmer_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class SQLGenerationResponse(BaseModel):
    """SQL generation response"""
    sql_query: str
    confidence: float
    validated: bool
    validation_errors: List[str] = Field(default_factory=list)
    execution_plan: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    """SQL validation result"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    query_type: str  # SELECT, INSERT, UPDATE, DELETE
    tables_accessed: List[str] = Field(default_factory=list)
