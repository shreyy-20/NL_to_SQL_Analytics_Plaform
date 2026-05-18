"""
Dashboard API endpoints for quick operational summaries.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db_connection import get_db_dependency
from backend.services.farmer_service import FarmerService, QueryLog

router = APIRouter()
farmer_service = FarmerService()


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db_dependency)) -> Dict[str, Any]:
    """Return top-level counters used by the frontend dashboard."""
    total_farmers = db.query(func.count(farmer_service.Farmer.farmer_id)).scalar() or 0
    total_queries = db.query(func.count(QueryLog.log_id)).scalar() or 0
    successful_queries = db.query(func.count(QueryLog.log_id)).filter(QueryLog.success.is_(True)).scalar() or 0
    avg_land_size = db.query(func.avg(farmer_service.Farmer.land_size)).scalar() or 0

    pmkisan_total = db.query(func.sum(farmer_service.PMKISANPayment.amount)).scalar() or 0
    kalia_total = db.query(func.sum(farmer_service.KALIAPayment.amount)).scalar() or 0

    return {
        "total_farmers": int(total_farmers),
        "total_queries": int(total_queries),
        "successful_queries": int(successful_queries),
        "average_land_size_hectares": float(avg_land_size),
        "total_payments_disbursed": float(pmkisan_total + kalia_total),
    }


@router.get("/charts")
async def get_charts(db: Session = Depends(get_db_dependency)) -> Dict[str, List[Dict[str, Any]]]:
    """Return chart-friendly grouped data."""
    district_rows = (
        db.query(
            farmer_service.Farmer.district,
            func.count(farmer_service.Farmer.farmer_id).label("count"),
        )
        .group_by(farmer_service.Farmer.district)
        .order_by(func.count(farmer_service.Farmer.farmer_id).desc())
        .all()
    )

    crop_rows = (
        db.query(
            farmer_service.MandiPrice.crop,
            func.count(farmer_service.MandiPrice.id).label("count"),
        )
        .group_by(farmer_service.MandiPrice.crop)
        .order_by(func.count(farmer_service.MandiPrice.id).desc())
        .limit(10)
        .all()
    )

    return {
        "farmers_by_district": [
            {"district": district, "count": count} for district, count in district_rows
        ],
        "top_crops_in_mandi_data": [
            {"crop": crop, "count": count} for crop, count in crop_rows
        ],
    }


@router.get("/recent")
async def get_recent_queries(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_dependency),
) -> Dict[str, List[Dict[str, Any]]]:
    """Return recent query log entries."""
    rows = db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
    return {
        "queries": [
            {
                "log_id": row.log_id,
                "phone_number": row.phone_number,
                "question": row.question,
                "intent": row.intent,
                "success": row.success,
                "timestamp": row.timestamp,
            }
            for row in rows
        ]
    }
