"""
Farmer management API endpoints.
"""

from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db_connection import get_db_dependency
from backend.models.farmer import FarmerListResponse, FarmerResponse, PaymentResponse
from backend.services.farmer_service import FarmerService

logger = logging.getLogger(__name__)
router = APIRouter()
farmer_service = FarmerService()


def _serialize_payment(payment) -> PaymentResponse:
    """Map ORM payment objects to the API response model."""
    is_pmkisan = isinstance(payment, farmer_service.PMKISANPayment)
    return PaymentResponse(
        payment_id=payment.id,
        farmer_id=payment.farmer_id,
        scheme_name="pmkisan" if is_pmkisan else "kalia",
        amount=payment.amount,
        payment_date=payment.payment_date,
        status=payment.status,
        transaction_id=payment.transaction_id,
        installment_number=getattr(payment, "installment_number", None),
        scheme_type=getattr(payment, "scheme_type", None),
    )


@router.get("/", response_model=FarmerListResponse)
def list_farmers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    district: Optional[str] = Query(None, description="Filter by district"),
    village: Optional[str] = Query(None, description="Filter by village"),
    db: Session = Depends(get_db_dependency),
):
    """List all farmers with pagination and filtering."""
    try:
        query = db.query(farmer_service.Farmer)

        if district:
            query = query.filter(farmer_service.Farmer.district == district)
        if village:
            query = query.filter(farmer_service.Farmer.village == village)

        total = query.count()
        farmers = query.order_by(farmer_service.Farmer.name).offset(skip).limit(limit).all()

        return FarmerListResponse(
            total=total,
            skip=skip,
            limit=limit,
            farmers=[FarmerResponse.model_validate(f) for f in farmers],
        )
    except Exception as exc:
        logger.error("Error listing farmers: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/search/by-name", response_model=List[FarmerResponse])
def search_farmers_by_name(
    name: str = Query(..., min_length=2, description="Farmer name to search"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db_dependency),
):
    """Search farmers by partial name match."""
    try:
        farmers = (
            db.query(farmer_service.Farmer)
            .filter(farmer_service.Farmer.name.ilike(f"%{name}%"))
            .limit(limit)
            .all()
        )
        return [FarmerResponse.model_validate(f) for f in farmers]
    except Exception as exc:
        logger.error("Error searching farmers by name %s: %s", name, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/districts/list")
def get_districts(db: Session = Depends(get_db_dependency)):
    """Get list of all districts in the database."""
    try:
        districts = (
            db.query(farmer_service.Farmer.district)
            .distinct()
            .order_by(farmer_service.Farmer.district)
            .all()
        )
        return [district[0] for district in districts if district[0]]
    except Exception as exc:
        logger.error("Error getting districts: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/statistics/summary")
def get_farmer_statistics(db: Session = Depends(get_db_dependency)):
    """Get summary statistics about farmers and market data."""
    try:
        total_farmers = db.query(func.count(farmer_service.Farmer.farmer_id)).scalar() or 0

        farmers_by_district = (
            db.query(
                farmer_service.Farmer.district,
                func.count(farmer_service.Farmer.farmer_id).label("count"),
            )
            .group_by(farmer_service.Farmer.district)
            .all()
        )

        avg_land_size = db.query(func.avg(farmer_service.Farmer.land_size)).scalar()

        top_crops = (
            db.query(
                farmer_service.MandiPrice.crop,
                func.count(farmer_service.MandiPrice.id).label("count"),
            )
            .group_by(farmer_service.MandiPrice.crop)
            .order_by(func.count(farmer_service.MandiPrice.id).desc())
            .limit(5)
            .all()
        )

        return {
            "total_farmers": total_farmers,
            "farmers_by_district": [
                {"district": district, "count": count}
                for district, count in farmers_by_district
            ],
            "average_land_size_hectares": float(avg_land_size) if avg_land_size else 0,
            "top_crops": [{"crop": crop, "records": count} for crop, count in top_crops],
        }
    except Exception as exc:
        logger.error("Error getting statistics: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{farmer_id}/payments", response_model=List[PaymentResponse])
def get_farmer_payments(
    farmer_id: int,
    scheme: Optional[str] = Query(None, description="Filter by scheme (pmkisan/kalia)"),
    limit: int = Query(50, ge=1, le=200, description="Number of payments to return"),
    db: Session = Depends(get_db_dependency),
):
    """Get payment history for a farmer."""
    try:
        farmer = db.query(farmer_service.Farmer).filter(
            farmer_service.Farmer.farmer_id == farmer_id
        ).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")

        payments = farmer_service.get_farmer_payments(db, farmer_id, scheme, limit)
        return [_serialize_payment(payment) for payment in payments]
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error getting payments for farmer %s: %s", farmer_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{farmer_id}/soil-health")
def get_soil_health(
    farmer_id: int,
    db: Session = Depends(get_db_dependency),
):
    """Get the latest soil health report for a farmer."""
    try:
        soil_health = farmer_service.get_farmer_soil_health(db, farmer_id)
        if not soil_health:
            raise HTTPException(status_code=404, detail="Soil health record not found")

        ph_value = soil_health.ph if soil_health.ph is not None else 0
        return {
            "farmer_id": farmer_id,
            "test_date": soil_health.test_date,
            "nitrogen": soil_health.nitrogen,
            "phosphorus": soil_health.phosphorus,
            "potassium": soil_health.potassium,
            "ph": soil_health.ph,
            "organic_carbon": soil_health.organic_carbon,
            "recommendation": soil_health.recommendation,
            "status": "healthy" if 6.0 <= ph_value <= 7.5 else "needs_attention",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error getting soil health for farmer %s: %s", farmer_id, exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{phone}", response_model=FarmerResponse)
def get_farmer_by_phone(
    phone: str = Path(..., pattern=r"^[6-9]\d{9}$"),
    db: Session = Depends(get_db_dependency),
):
    """Get farmer details by 10-digit phone number."""
    try:
        farmer = farmer_service.get_farmer_by_phone(db, phone)
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        return FarmerResponse.model_validate(farmer)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error getting farmer %s: %s", phone, exc)
        raise HTTPException(status_code=500, detail=str(exc))
