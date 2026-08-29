"""
Escalation Policy, Tiered Manager Routing, and Escalation Trigger Service.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import EntityNotFoundError
from app.models.case import Case, CaseTimelineEvent
from app.models.escalation import EscalationPolicy, EscalationEvent
from app.models.agent import Agent, Team
from app.schemas.escalation import EscalationPolicyCreate, EscalationEventResponse


class EscalationService:
    @staticmethod
    async def create_policy(session: AsyncSession, data: EscalationPolicyCreate) -> EscalationPolicy:
        policy = EscalationPolicy(
            name=data.name,
            description=data.description,
            trigger_type=data.trigger_type,
            threshold_value=data.threshold_value,
            escalate_to_role=data.escalate_to_role,
            target_team_id=data.target_team_id,
            notify_managers=data.notify_managers,
            is_active=data.is_active,
        )
        session.add(policy)
        await session.commit()
        await session.refresh(policy)
        return policy

    @staticmethod
    async def escalate_case(
        session: AsyncSession,
        case_id: str,
        reason: str,
        actor_id: Optional[str] = None,
        escalate_to_role: str = "TEAM_LEAD",
        notes: Optional[str] = None,
        event_bus: Optional[EventBus] = None,
    ) -> EscalationEvent:
        case = await session.scalar(select(Case).where(Case.id == case_id))
        if not case:
            raise EntityNotFoundError("Case", case_id)

        case.is_escalated = True
        case.status = "ESCALATED"
        if case.priority in ["LOW", "MEDIUM"]:
            case.priority = "HIGH"

        escalation_event = EscalationEvent(
            case_id=case.id,
            escalation_reason=reason,
            escalation_level=2 if escalate_to_role == "MANAGER" else 1,
            escalated_by_id=actor_id,
            notes=notes,
            status="OPEN",
        )
        session.add(escalation_event)

        # Timeline event
        t_event = CaseTimelineEvent(
            case_id=case.id,
            actor_id=actor_id,
            actor_type="AGENT" if actor_id else "SYSTEM",
            event_type="ESCALATED",
            summary=f"Case escalated to {escalate_to_role}: {reason}",
            previous_value=case.assigned_agent_id,
            new_value=f"ROLE:{escalate_to_role}",
        )
        session.add(t_event)
        await session.commit()
        await session.refresh(escalation_event)

        # Emit Event
        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.CASE_ESCALATED,
                actor={"user_id": actor_id},
                payload={
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "reason": reason,
                    "escalate_to_role": escalate_to_role,
                },
            )
        )
        return escalation_event
