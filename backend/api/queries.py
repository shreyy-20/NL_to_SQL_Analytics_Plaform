import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import time
import uuid

from backend.db_connection import get_db_dependency
from backend.models.query import QueryRequest, QueryResponse
from backend.services.query_service import QueryService
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
query_service = QueryService()

@router.post("/", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_dependency)
):
    try:
        # Validate phone number
        if not request.phone_number or len(request.phone_number) != 10:
            return QueryResponse(
                success=False,
                answer="????? ??? 10 ????? ?? ?????? ???? ??????",
                error="Invalid phone number"
            )
        
        logger.info(f"Processing query: {request.question[:50]}... for phone: {request.phone_number}")
        
        # Process the query
        result = await query_service.process_query(
            db=db,
            question=request.question,
            phone_number=request.phone_number,
            language=request.language
        )
        
        return QueryResponse(
            success=result.success,
            answer=result.answer,
            data=result.data,
            intent=result.intent,
            confidence=result.confidence,
            processing_time_ms=result.processing_time_ms,
            query_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return QueryResponse(
            success=False,
            answer="????? ????, ???? ?????? ??????? ???? ??? ?????? ???? ????? ???? ?????? ?????",
            error=str(e),
            processing_time_ms=0
        )
