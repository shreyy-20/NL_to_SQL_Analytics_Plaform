from pydantic import BaseModel
from typing import Optional, Any

class QueryRequest(BaseModel):
    phone_number: Optional[str]
    question: str
    language: Optional[str] = "hi"

class QueryResult(BaseModel):
    sql: str
    data: Any

class QueryResponse(BaseModel):
    intent: str
    result: QueryResult
    message: str