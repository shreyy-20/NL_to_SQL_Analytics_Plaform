"""
Farmer related Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class FarmerBase(BaseModel):
    """Base farmer model"""
    name: str = Field(..., min_length=2, max_length=100, description="Farmer's full name")
    phone: str = Field(..., pattern=r'^[6-9]\d{9}$', description="10-digit mobile number")
    village: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=50)
    state: str = Field(default="Odisha", max_length=50)
    land_size: Optional[float] = Field(None, ge=0, le=100, description="Land size in hectares")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('Phone number must contain only digits')
        if len(v) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v

class FarmerCreate(FarmerBase):
    """Model for creating a new farmer"""
    pass

class FarmerResponse(FarmerBase):
    """Model for farmer API response"""
    farmer_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FarmerWithPayments(FarmerResponse):
    """Farmer response including payment history"""
    total_pmkisan_received: Optional[Decimal] = Field(0, description="Total PM-KISAN amount received")
    total_kalia_received: Optional[Decimal] = Field(0, description="Total KALIA amount received")
    last_payment_date: Optional[datetime] = None
    next_payment_due: Optional[datetime] = None
    
class PaymentBase(BaseModel):
    """Base payment model"""
    farmer_id: int
    scheme_name: str = Field(..., pattern='^(pmkisan|kalia)$')
    amount: Decimal = Field(..., gt=0, description="Payment amount in INR")
    payment_date: datetime
    status: str = Field(..., pattern='^(pending|processed|completed|failed)$')
    transaction_id: Optional[str] = None
    installment_number: Optional[int] = None
    scheme_type: Optional[str] = None

class PaymentResponse(PaymentBase):
    """Payment API response model"""
    payment_id: int
    
    class Config:
        from_attributes = True

class SoilHealthBase(BaseModel):
    """Base soil health model"""
    farmer_id: int
    nitrogen: Optional[float] = Field(None, ge=0, le=500, description="Nitrogen (kg/ha)")
    phosphorus: Optional[float] = Field(None, ge=0, le=200, description="Phosphorus (kg/ha)")
    potassium: Optional[float] = Field(None, ge=0, le=500, description="Potassium (kg/ha)")
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH")
    organic_carbon: Optional[float] = Field(None, ge=0, le=10, description="Organic carbon (%)")
    test_date: datetime
    recommendation: Optional[str] = None

class SoilHealthResponse(SoilHealthBase):
    """Soil health API response model"""
    report_id: int
    
    class Config:
        from_attributes = True

class MandiPriceBase(BaseModel):
    """Base mandi price model"""
    crop: str
    market: str
    district: str
    price: Decimal = Field(..., gt=0, description="Price per quintal")
    date: datetime
    variety: Optional[str] = None
    grade: Optional[str] = None

class MandiPriceResponse(MandiPriceBase):
    """Mandi price API response model"""
    price_id: int
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    """Natural language query request"""
    question: str = Field(..., min_length=3, max_length=500)
    phone_number: str = Field(..., pattern=r'^[6-9]\d{9}$')
    language: str = Field(default="hi", pattern='^(hi|or|en)$')
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    answer: str
    data: Optional[dict] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None
    query_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class QueryLog(BaseModel):
    """Model for logging queries to database"""
    log_id: Optional[int] = None
    phone_number: str
    question: str
    intent: str
    sql_generated: Optional[str] = None
    response: str
    success: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

class FarmerListResponse(BaseModel):
    """Paginated farmer list response"""
    total: int
    skip: int
    limit: int
    farmers: List[FarmerResponse]

class FarmerCrop(BaseModel):
    """Model for farmer crop association"""
    farmer_id: int
    crop_name: str
    area_hectares: Optional[float] = None
    season: Optional[str] = Field(None, pattern='^(kharif|rabi|zaid)$')
