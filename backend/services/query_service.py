from sqlalchemy.orm import Session

def process_natural_language_query(db: Session, question: str):
    # TEMP logic (Phase 2 will replace this with AI pipeline)

    if "payment" in question.lower():
        sql = "SELECT * FROM pmkisan_payments LIMIT 5"
        intent = "PAYMENT"
    elif "price" in question.lower():
        sql = "SELECT * FROM mandi_prices LIMIT 5"
        intent = "PRICE"
    else:
        sql = "SELECT * FROM farmers LIMIT 5"
        intent = "GENERAL"

    result = db.execute(sql).fetchall()
    data = [dict(r._mapping) for r in result]

    return {
        "intent": intent,
        "sql": sql,
        "data": data,
        "message": "Query processed successfully"
    }