from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db_connection import get_db
from backend.services.farmer_service import (
    get_farmer_by_phone,
    get_all_farmers,
    get_farmer_payments
)

router = APIRouter(prefix="/farmers", tags=["Farmers"])

@router.get("/{phone}")
def get_farmer(phone: str, db: Session = Depends(get_db)):
    farmer = get_farmer_by_phone(db, phone)
    return farmer or {"error": "Farmer not found"}


@router.get("/")
def list_farmers(db: Session = Depends(get_db)):
    return get_all_farmers(db)


@router.get("/{farmer_id}/payments")
def payments(farmer_id: int, db: Session = Depends(get_db)):
    return get_farmer_payments(db, farmer_id)