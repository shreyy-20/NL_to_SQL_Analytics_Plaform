"""
Farmer service for business logic related to farmers
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from backend.db_connection import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

logger = logging.getLogger(__name__)

# Define ORM models correctly for SQLAlchemy 2.0
class Farmer(Base):
    __tablename__ = "farmers"
    
    farmer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="Odisha")
    land_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PMKISANPayment(Base):
    __tablename__ = "pmkisan_payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.farmer_id"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    installment_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class KALIAPayment(Base):
    __tablename__ = "kalia_payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.farmer_id"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    scheme_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SoilHealth(Base):
    __tablename__ = "soil_health"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.farmer_id"))
    nitrogen: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    phosphorus: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    potassium: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ph: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    organic_carbon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    test_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class MandiPrice(Base):
    __tablename__ = "mandi_prices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop: Mapped[str] = mapped_column(String(50), nullable=False)
    market: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Weather(Base):
    __tablename__ = "weather"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    rainfall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    forecast: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    __tablename__ = "query_logs"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sql_generated: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FarmerService:
    """Service class for farmer-related operations"""
    
    def __init__(self):
        self.Farmer = Farmer
        self.PMKISANPayment = PMKISANPayment
        self.KALIAPayment = KALIAPayment
        self.SoilHealth = SoilHealth
        self.MandiPrice = MandiPrice
        self.Weather = Weather
        self.QueryLog = QueryLog
    
    def get_farmer_by_phone(self, db: Session, phone: str) -> Optional[Farmer]:
        """Get farmer by phone number"""
        try:
            farmer = db.query(self.Farmer).filter(
                self.Farmer.phone == phone
            ).first()
            return farmer
        except Exception as e:
            logger.error(f"Error getting farmer by phone {phone}: {e}")
            return None
    
    def get_farmer_by_id(self, db: Session, farmer_id: int) -> Optional[Farmer]:
        """Get farmer by ID"""
        try:
            farmer = db.query(self.Farmer).filter(
                self.Farmer.farmer_id == farmer_id
            ).first()
            return farmer
        except Exception as e:
            logger.error(f"Error getting farmer by ID {farmer_id}: {e}")
            return None
    
    def get_farmer_payments(
        self, 
        db: Session, 
        farmer_id: int, 
        scheme: Optional[str] = None,
        limit: int = 50
    ) -> List:
        """Get payment history for a farmer"""
        payments = []
        
        try:
            if not scheme or scheme.lower() == "pmkisan":
                pm_payments = db.query(self.PMKISANPayment).filter(
                    self.PMKISANPayment.farmer_id == farmer_id
                ).order_by(desc(self.PMKISANPayment.payment_date)).limit(limit).all()
                payments.extend(pm_payments)
            
            if not scheme or scheme.lower() == "kalia":
                kalia_payments = db.query(self.KALIAPayment).filter(
                    self.KALIAPayment.farmer_id == farmer_id
                ).order_by(desc(self.KALIAPayment.payment_date)).limit(limit).all()
                payments.extend(kalia_payments)
            
            # Sort combined list by date
            payments.sort(key=lambda x: x.payment_date, reverse=True)
            
            return payments[:limit]
        except Exception as e:
            logger.error(f"Error getting payments for farmer {farmer_id}: {e}")
            return []
    
    def get_farmer_soil_health(self, db: Session, farmer_id: int) -> Optional[SoilHealth]:
        """Get latest soil health report for a farmer"""
        try:
            soil_health = db.query(self.SoilHealth).filter(
                self.SoilHealth.farmer_id == farmer_id
            ).order_by(desc(self.SoilHealth.test_date)).first()
            return soil_health
        except Exception as e:
            logger.error(f"Error getting soil health for farmer {farmer_id}: {e}")
            return None
