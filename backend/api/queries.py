from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db_connection import get_db
from backend.models.query import QueryRequest
from backend.services.query_service import process_natural_language_query

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/")
def query(request: QueryRequest, db: Session = Depends(get_db)):
    result = process_natural_language_query(db, request.question)
    return result