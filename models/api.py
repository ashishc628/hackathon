# app/models/api.py
from pydantic import BaseModel
from typing import Any, Optional

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    route: str
    raw_stats: Optional[Any] = None  # Optional: for debugging/analytics view
