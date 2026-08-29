"""
AI Triage, Classification, Suggested Replies, and Vector RAG schemas.
"""

from typing import List, Optional
from app.schemas.common import BaseSchema


class AIClassificationRequest(BaseSchema):
    text: str
    order_id: Optional[str] = None
    customer_tier: Optional[str] = "STANDARD"


class AIClassificationResponse(BaseSchema):
    intent: str
    suggested_category: str
    suggested_subcategory: Optional[str] = None
    suggested_priority: str
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str  # POSITIVE, NEUTRAL, NEGATIVE, HIGHLY_FRUSTRATED
    confidence_score: float
    summary: str
    recommended_playbook_code: Optional[str] = None


class AISuggestedReplyResponse(BaseSchema):
    reply_text: str
    confidence: float
    suggested_playbook_code: Optional[str] = None
    source_articles: List[str] = []


class VectorQueryRequest(BaseSchema):
    query: str
    top_k: int = 4
    source_type: Optional[str] = None


class VectorSearchResultItem(BaseSchema):
    source_type: str
    source_id: str
    content: str
    score: float
    metadata_json: Optional[dict] = None


class VectorSearchResponse(BaseSchema):
    query: str
    results: List[VectorSearchResultItem]
