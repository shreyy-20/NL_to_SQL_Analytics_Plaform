from sqlalchemy.orm import Session
from sqlalchemy import text

def get_farmer_by_phone(db: Session, phone: str):
    query = text("SELECT * FROM farmers WHERE phone = :phone")
    result = db.execute(query, {"phone": phone}).fetchone()
    return dict(result._mapping) if result else None


def get_all_farmers(db: Session):
    query = text("SELECT * FROM farmers LIMIT 100")
    results = db.execute(query).fetchall()
    return [dict(r._mapping) for r in results]


def get_farmer_payments(db: Session, farmer_id: int):
    query = text("""
        SELECT * FROM pmkisan_payments
        WHERE farmer_id = :farmer_id
    """)
    results = db.execute(query, {"farmer_id": farmer_id}).fetchall()
    return [dict(r._mapping) for r in results]