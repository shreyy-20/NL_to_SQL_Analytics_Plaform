#!/usr/bin/env python3
"""
Seed data loader for KrishiQuery.
Loads sample CSV data into the database while skipping placeholder rows.
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db_connection import SessionLocal
from backend.services.farmer_service import (
    Farmer,
    KALIAPayment,
    MandiPrice,
    PMKISANPayment,
    SoilHealth,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "sample_data"


def _clean_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _is_placeholder_row(row: Dict[str, str]) -> bool:
    for value in row.values():
        text = _clean_str(value)
        if text and "continue to" in text.lower():
            return True
    return False


def _to_int(value: Optional[str]) -> Optional[int]:
    text = _clean_str(value)
    if text is None:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _to_float(value: Optional[str]) -> Optional[float]:
    text = _clean_str(value)
    if text is None:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _to_date(value: Optional[str]):
    text = _clean_str(value)
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def _to_phone(value: Optional[str]) -> Optional[str]:
    as_int = _to_int(value)
    if as_int is None:
        text = _clean_str(value)
        if text and text.isdigit():
            return text
        return None
    return str(as_int)


def _iter_rows(csv_path: Path) -> Iterable[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if _is_placeholder_row(row):
                continue
            yield row


def load_farmers(session) -> int:
    csv_path = DATA_DIR / "farmers_odisha.csv"
    if not csv_path.exists():
        logger.warning("Farmers CSV not found: %s", csv_path)
        return 0

    count = 0
    for row in _iter_rows(csv_path):
        farmer_id = _to_int(row.get("farmer_id"))
        phone = _to_phone(row.get("phone"))
        name = _clean_str(row.get("name"))
        village = _clean_str(row.get("village"))
        district = _clean_str(row.get("district"))

        if not all([farmer_id, phone, name, village, district]):
            continue

        farmer = Farmer(
            farmer_id=farmer_id,
            name=name,
            phone=phone,
            village=village,
            district=district,
            land_size=_to_float(row.get("land_size")),
        )
        session.merge(farmer)
        count += 1

    session.commit()
    logger.info("Loaded %s farmers", count)
    return count


def load_pmkisan_payments(session) -> int:
    csv_path = DATA_DIR / "pmkisan_payments.csv"
    if not csv_path.exists():
        logger.warning("PM-KISAN CSV not found: %s", csv_path)
        return 0

    count = 0
    for row in _iter_rows(csv_path):
        record_id = _to_int(row.get("id"))
        farmer_id = _to_int(row.get("farmer_id"))
        amount = _to_float(row.get("amount"))
        payment_date = _to_date(row.get("payment_date"))

        if not all([record_id, farmer_id, amount is not None, payment_date]):
            continue

        payment = PMKISANPayment(
            id=record_id,
            farmer_id=farmer_id,
            amount=amount,
            payment_date=payment_date,
            status=_clean_str(row.get("status")) or "pending",
            transaction_id=_clean_str(row.get("transaction_id")),
            installment_number=_to_int(row.get("installment_number")),
        )
        session.merge(payment)
        count += 1

    session.commit()
    logger.info("Loaded %s PM-KISAN payments", count)
    return count


def load_kalia_payments(session) -> int:
    csv_path = DATA_DIR / "kalia_payments.csv"
    if not csv_path.exists():
        logger.warning("KALIA CSV not found: %s", csv_path)
        return 0

    count = 0
    for row in _iter_rows(csv_path):
        record_id = _to_int(row.get("id"))
        farmer_id = _to_int(row.get("farmer_id"))
        amount = _to_float(row.get("amount"))
        payment_date = _to_date(row.get("payment_date"))

        if not all([record_id, farmer_id, amount is not None, payment_date]):
            continue

        payment = KALIAPayment(
            id=record_id,
            farmer_id=farmer_id,
            amount=amount,
            payment_date=payment_date,
            status=_clean_str(row.get("status")) or "pending",
            transaction_id=_clean_str(row.get("transaction_id")),
            scheme_type=_clean_str(row.get("scheme_type")),
        )
        session.merge(payment)
        count += 1

    session.commit()
    logger.info("Loaded %s KALIA payments", count)
    return count


def load_soil_health(session) -> int:
    csv_path = DATA_DIR / "soil_health_odisha.csv"
    if not csv_path.exists():
        logger.warning("Soil Health CSV not found: %s", csv_path)
        return 0

    count = 0
    for row in _iter_rows(csv_path):
        record_id = _to_int(row.get("id"))
        farmer_id = _to_int(row.get("farmer_id"))
        test_date = _to_date(row.get("test_date"))

        if not all([record_id, farmer_id, test_date]):
            continue

        soil = SoilHealth(
            id=record_id,
            farmer_id=farmer_id,
            nitrogen=_to_float(row.get("nitrogen")),
            phosphorus=_to_float(row.get("phosphorus")),
            potassium=_to_float(row.get("potassium")),
            ph=_to_float(row.get("ph")),
            organic_carbon=_to_float(row.get("organic_carbon")),
            test_date=test_date,
            recommendation=_clean_str(row.get("recommendation")),
        )
        session.merge(soil)
        count += 1

    session.commit()
    logger.info("Loaded %s soil health records", count)
    return count


def load_mandi_prices(session) -> int:
    csv_path = DATA_DIR / "mandi_prices_odisha.csv"
    if not csv_path.exists():
        logger.warning("Mandi Prices CSV not found: %s", csv_path)
        return 0

    count = 0
    for row in _iter_rows(csv_path):
        record_id = _to_int(row.get("id"))
        crop = _clean_str(row.get("crop"))
        market = _clean_str(row.get("market"))
        district = _clean_str(row.get("district"))
        price = _to_float(row.get("price"))
        date_value = _to_date(row.get("date"))

        if not all([record_id, crop, market, district, price is not None, date_value]):
            continue

        price_row = MandiPrice(
            id=record_id,
            crop=crop,
            market=market,
            district=district,
            price=price,
            date=date_value,
            variety=_clean_str(row.get("variety")),
            grade=_clean_str(row.get("grade")),
        )
        session.merge(price_row)
        count += 1

    session.commit()
    logger.info("Loaded %s mandi price records", count)
    return count


def seed_all() -> None:
    session = SessionLocal()
    try:
        load_farmers(session)
        load_pmkisan_payments(session)
        load_kalia_payments(session)
        load_soil_health(session)
        load_mandi_prices(session)
        logger.info("All sample data loaded successfully")
    except Exception as exc:
        logger.error("Seeding failed: %s", exc)
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Seed KrishiQuery database")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    if args.clear:
        confirm = input("This will delete ALL existing data. Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Aborted")
            return

    seed_all()


if __name__ == "__main__":
    main()
