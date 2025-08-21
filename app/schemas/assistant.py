from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class Country(str, Enum):
    CZECH_REPUBLIC = "czech_republic"


class ChatRequest(BaseModel):
    message: str
    country: Country = Country.CZECH_REPUBLIC
    user_background: Dict[str, Any] = {}
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    response: str
    query: str
    country: Country
    user_background: Dict[str, Any]
    session_id: str
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
