"""
Customer Intelligence, Frustration, and Churn Risk schemas.
"""

from datetime import datetime
from typing import Optional
from app.schemas.common import BaseSchema


class FrustrationScoreResponse(BaseSchema):
    customer_id: str
    case_id: Optional[str] = None
    frustration_score: float  # 0 to 100
    sentiment_index: float  # -1.0 to 1.0
    repeat_contact_count_7d: int
    unresolved_cases_count: int
    sla_breaches_count: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors_json: Optional[dict] = None


class ChurnRiskResponse(BaseSchema):
    customer_id: str
    churn_probability: float
    predicted_risk_tier: str
    mitigation_recommendation: Optional[str] = None
    last_evaluated_at: datetime
