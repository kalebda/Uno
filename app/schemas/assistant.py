from typing import Any, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_background: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    response: str
    query: str
    user_background: Dict[str, Any]
    sources: list = []
    confidence: float = 0.0
    error: bool = False


class ScholarshipAnalysisRequest(BaseModel):
    user_background: Dict[str, Any]
    scholarship_query: str = None


class ScholarshipAnalysisResponse(BaseModel):
    analysis: str
    user_background: Dict[str, Any]
    scholarship_query: str = None
    sources: list = []
    confidence: float = 0.0
    error: bool = False
