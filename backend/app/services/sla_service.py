"""
SLA Policy Management, Deadline Tracking, Pause/Resume, and Breach Evaluator.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.config import settings
from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.telemetry import MetricsService
from app.models.case import Case, CaseTimelineEvent
from app.models.sla import SLAPolicy, SLATracker, SLAPauseLog, SLABreachLog
from app.models.customer import Customer
from app.schemas.sla import SLAPolicyCreate


class SLAService:
    @staticmethod
    async def create_policy(session: AsyncSession, data: SLAPolicyCreate) -> SLAPolicy:
        policy = SLAPolicy(
            name=data.name,
            description=data.description,
            priority=data.priority,
            category=data.category,
            customer_tier=data.customer_tier,
            first_response_time_mins=data.first_response_time_mins,
            resolution_time_hours=data.resolution_time_hours,
            warning_threshold_percent=data.warning_threshold_percent,
            use_business_hours=data.use_business_hours,
            business_hours_start=data.business_hours_start,
            business_hours_end=data.business_hours_end,
            timezone=data.timezone,
            is_active=data.is_active,
        )
        session.add(policy)
        await session.commit()
        await session.refresh(policy)
        return policy

    @staticmethod
    async def find_matching_policy(session: AsyncSession, case: Case) -> SLAPolicy:
        """Find the best-fitting SLA policy for a case."""
        policies = await session.scalars(
            select(SLAPolicy).where(SLAPolicy.is_active == True)
        )
        all_p = list(policies.all())

        # Exact priority match
        for p in all_p:
            if p.priority == case.priority and (p.category in ["ALL", case.category]):
                return p

        # Fallback to default policy or create standard default
        fallback = next((p for p in all_p if p.priority == "ALL"), None)
        if fallback:
            return fallback

        # If no policy in DB, create on the fly from settings
        default_policy = SLAPolicy(
            name=f"Default {case.priority} Policy",
            priority=case.priority,
            category="ALL",
            first_response_time_mins=(
                settings.SLA_CRITICAL_FIRST_RESPONSE_MINS if case.priority == "CRITICAL"
                else settings.SLA_HIGH_FIRST_RESPONSE_MINS if case.priority == "HIGH"
                else settings.SLA_MEDIUM_FIRST_RESPONSE_MINS
            ),
            resolution_time_hours=(
                settings.SLA_CRITICAL_RESOLUTION_HOURS if case.priority == "CRITICAL"
                else settings.SLA_HIGH_RESOLUTION_HOURS if case.priority == "HIGH"
                else settings.SLA_MEDIUM_RESOLUTION_HOURS
            ),
            is_active=True,
        )
        session.add(default_policy)
        await session.flush()
        return default_policy

    @staticmethod
    async def start_sla_tracker(
        session: AsyncSession, case_id: str, event_bus: Optional[EventBus] = None
    ) -> SLATracker:
        case = await session.scalar(select(Case).where(Case.id == case_id))
        if not case:
            raise ValueError(f"Case {case_id} not found")

        policy = await SLAService.find_matching_policy(session, case)
        now = datetime.now(timezone.utc)

        first_resp_due = now + timedelta(minutes=policy.first_response_time_mins)
        resolution_due = now + timedelta(hours=policy.resolution_time_hours)

        case.first_response_due_at = first_resp_due
        case.resolution_due_at = resolution_due

        tracker = SLATracker(
            case_id=case.id,
            policy_id=policy.id,
            first_response_due_at=first_resp_due,
            resolution_due_at=resolution_due,
        )
        session.add(tracker)
        await session.commit()
        await session.refresh(tracker)

        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.SLA_STARTED,
                payload={
                    "case_id": case.id,
                    "policy_id": policy.id,
                    "first_response_due_at": first_resp_due.isoformat(),
                    "resolution_due_at": resolution_due.isoformat(),
                },
            )
        )
        return tracker

    @staticmethod
    async def handle_status_change(
        session: AsyncSession, case_id: str, new_status: str, actor_id: Optional[str] = None
    ) -> None:
        """Pause SLA when waiting for customer/external systems, resume when back in progress."""
        tracker = await session.scalar(
            select(SLATracker).where(SLATracker.case_id == case_id).order_by(SLATracker.created_at.desc())
        )
        if not tracker:
            return

        now = datetime.now(timezone.utc)
        if new_status in ["WAITING_FOR_CUSTOMER", "WAITING_FOR_EXTERNAL_SYSTEM"] and not tracker.is_paused:
            tracker.is_paused = True
            tracker.paused_at = now
            pause_log = SLAPauseLog(
                tracker_id=tracker.id,
                paused_at=now,
                pause_reason=new_status,
                paused_by=actor_id,
            )
            session.add(pause_log)
            await session.commit()

        elif new_status in ["OPEN", "IN_PROGRESS"] and tracker.is_paused:
            tracker.is_paused = False
            if tracker.paused_at:
                paused_dt = tracker.paused_at.replace(tzinfo=timezone.utc) if tracker.paused_at.tzinfo is None else tracker.paused_at
                delta_secs = int((now - paused_dt).total_seconds())
                tracker.total_paused_seconds += delta_secs
                # Extend deadlines by pause duration
                tracker.first_response_due_at += timedelta(seconds=delta_secs)
                tracker.resolution_due_at += timedelta(seconds=delta_secs)

                # Close active pause log
                pause_log = await session.scalar(
                    select(SLAPauseLog)
                    .where(SLAPauseLog.tracker_id == tracker.id, SLAPauseLog.resumed_at == None)
                    .order_by(SLAPauseLog.paused_at.desc())
                )
                if pause_log:
                    pause_log.resumed_at = now

            tracker.paused_at = None
            await session.commit()

    @staticmethod
    async def evaluate_active_slas(
        session: AsyncSession, event_bus: Optional[EventBus] = None
    ) -> dict:
        """Scheduled background task inspecting active SLA trackers for warnings and breaches."""
        now = datetime.now(timezone.utc)
        trackers = await session.scalars(
            select(SLATracker)
            .join(Case, Case.id == SLATracker.case_id)
            .where(
                Case.status.in_(["NEW", "OPEN", "IN_PROGRESS", "ESCALATED"]),
                SLATracker.is_paused == False,
            )
        )
        all_trackers = list(trackers.all())
        bus = event_bus or get_event_bus()

        warnings_count = 0
        breaches_count = 0

        for t in all_trackers:
            case = await session.scalar(select(Case).where(Case.id == t.case_id))
            if not case:
                continue

            # 1. First response check
            first_due = t.first_response_due_at.replace(tzinfo=timezone.utc) if t.first_response_due_at.tzinfo is None else t.first_response_due_at
            if not case.first_responded_at and not t.is_first_response_breached:
                if now > first_due:
                    t.is_first_response_breached = True
                    breaches_count += 1
                    b_log = SLABreachLog(
                        tracker_id=t.id,
                        case_id=case.id,
                        breach_type="FIRST_RESPONSE",
                        due_at=t.first_response_due_at,
                        overdue_seconds=int((now - first_due).total_seconds()),
                    )
                    session.add(b_log)
                    MetricsService.record_sla_breach("Default", "FIRST_RESPONSE", case.priority)
                    await bus.publish(
                        Event(
                            topic=EventTopic.SLA_BREACHED,
                            payload={
                                "case_id": case.id,
                                "breach_type": "FIRST_RESPONSE",
                                "overdue_seconds": b_log.overdue_seconds,
                            },
                        )
                    )

            # 2. Resolution check
            res_due = t.resolution_due_at.replace(tzinfo=timezone.utc) if t.resolution_due_at.tzinfo is None else t.resolution_due_at
            if not case.resolved_at and not t.is_resolution_breached:
                if now > res_due:
                    t.is_resolution_breached = True
                    breaches_count += 1
                    b_log = SLABreachLog(
                        tracker_id=t.id,
                        case_id=case.id,
                        breach_type="RESOLUTION",
                        due_at=t.resolution_due_at,
                        overdue_seconds=int((now - res_due).total_seconds()),
                    )
                    session.add(b_log)
                    MetricsService.record_sla_breach("Default", "RESOLUTION", case.priority)
                    await bus.publish(
                        Event(
                            topic=EventTopic.SLA_BREACHED,
                            payload={
                                "case_id": case.id,
                                "breach_type": "RESOLUTION",
                                "overdue_seconds": b_log.overdue_seconds,
                            },
                        )
                    )

        await session.commit()
        return {"evaluated": len(all_trackers), "warnings": warnings_count, "breaches": breaches_count}
