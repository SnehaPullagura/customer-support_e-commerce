"""
Customer Intelligence, Frustration Score Algorithm, and Churn Risk Service.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.models.case import Case
from app.models.customer import Customer
from app.models.customer_intelligence import CustomerFrustrationScore, CustomerChurnRisk
from app.schemas.customer_intelligence import FrustrationScoreResponse, ChurnRiskResponse


class CustomerIntelligenceService:
    @staticmethod
    async def compute_frustration_score(
        session: AsyncSession, customer_id: str, case_id: Optional[str] = None
    ) -> FrustrationScoreResponse:
        customer = await session.scalar(select(Customer).where(Customer.id == customer_id))
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        # 1. Count repeat contacts in last 7 days
        repeat_contacts = await session.scalar(
            select(func.count(Case.id)).where(
                Case.customer_id == customer.id,
                Case.created_at >= seven_days_ago,
            )
        ) or 0

        # 2. Count unresolved open cases
        unresolved_cases = await session.scalar(
            select(func.count(Case.id)).where(
                Case.customer_id == customer.id,
                Case.status.in_(["NEW", "OPEN", "IN_PROGRESS", "ESCALATED"]),
            )
        ) or 0

        # 3. Latest sentiment score from current or past cases
        latest_case = None
        if case_id:
            latest_case = await session.scalar(select(Case).where(Case.id == case_id))
        if not latest_case:
            latest_case = await session.scalar(
                select(Case).where(Case.customer_id == customer.id).order_by(Case.created_at.desc())
            )

        sentiment_score = latest_case.sentiment_score if latest_case and latest_case.sentiment_score is not None else 0.0

        # 4. Multi-factor Frustration Algorithm:
        # Base: 10.0
        # Negative Sentiment penalty: up to +40 points
        # Repeat contact penalty: +15 points per contact in 7 days
        # Unresolved cases penalty: +10 points per case
        sentiment_penalty = max(0.0, -sentiment_score * 40.0)
        repeat_penalty = min(35.0, repeat_contacts * 12.0)
        unresolved_penalty = min(25.0, unresolved_cases * 10.0)

        raw_score = 10.0 + sentiment_penalty + repeat_penalty + unresolved_penalty
        frustration_score = min(100.0, max(0.0, raw_score))

        if frustration_score >= 75.0:
            risk_level = "CRITICAL"
        elif frustration_score >= 50.0:
            risk_level = "HIGH"
        elif frustration_score >= 25.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        factors = {
            "sentiment_score": sentiment_score,
            "repeat_contacts_7d": repeat_contacts,
            "unresolved_cases": unresolved_cases,
            "customer_tier": customer.tier,
        }

        # Save to DB
        score_record = CustomerFrustrationScore(
            customer_id=customer.id,
            case_id=case_id,
            frustration_score=round(frustration_score, 1),
            sentiment_index=sentiment_score,
            repeat_contact_count_7d=repeat_contacts,
            unresolved_cases_count=unresolved_cases,
            sla_breaches_count=0,
            risk_level=risk_level,
            factors_json=factors,
        )
        session.add(score_record)

        # Update case frustration score if case provided
        if latest_case:
            latest_case.frustration_score = score_record.frustration_score
            # If critical frustration, automatically escalate priority
            if risk_level == "CRITICAL" and latest_case.priority != "CRITICAL":
                latest_case.priority = "CRITICAL"

        await session.commit()

        return FrustrationScoreResponse(
            customer_id=customer.id,
            case_id=case_id,
            frustration_score=score_record.frustration_score,
            sentiment_index=score_record.sentiment_index,
            repeat_contact_count_7d=repeat_contacts,
            unresolved_cases_count=unresolved_cases,
            sla_breaches_count=0,
            risk_level=risk_level,
            factors_json=factors,
        )

    @staticmethod
    async def evaluate_churn_risk(session: AsyncSession, customer_id: str) -> ChurnRiskResponse:
        customer = await session.scalar(select(Customer).where(Customer.id == customer_id))
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        frust_resp = await CustomerIntelligenceService.compute_frustration_score(session, customer.id)
        
        # Churn probability model
        prob = min(0.99, (frust_resp.frustration_score / 100.0) * 0.85 + (0.10 if customer.tier == "VIP" else 0.05))
        risk_tier = "SEVERE" if prob > 0.70 else "ELEVATED" if prob > 0.40 else "LOW"

        recommendation = (
            "Offer $20 courtesy discount credit and assign senior retention specialist."
            if risk_tier == "SEVERE"
            else "Expedite replacement and prioritize case queue."
        )

        return ChurnRiskResponse(
            customer_id=customer.id,
            churn_probability=round(prob, 2),
            predicted_risk_tier=risk_tier,
            mitigation_recommendation=recommendation,
            last_evaluated_at=datetime.now(timezone.utc),
        )
