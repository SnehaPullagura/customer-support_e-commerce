"""
Immutable Security and Business Operation Audit Ledger Service.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.logging import get_correlation_id
from app.core.security import mask_sensitive_data
from app.models.audit import AuditEvent
from app.schemas.audit import AuditQueryFilter


class AuditService:
    @staticmethod
    async def log_event(
        session: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: str,
        description: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        actor_role: str = "SYSTEM",
        ip_address: Optional[str] = None,
        changes_json: Optional[dict] = None,
    ) -> AuditEvent:
        masked_desc = mask_sensitive_data(description)
        correlation_id = get_correlation_id()

        event = AuditEvent(
            actor_id=actor_id,
            actor_email=actor_email,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            correlation_id=correlation_id,
            description=masked_desc,
            changes_json=changes_json,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event

    @staticmethod
    async def query_logs(
        session: AsyncSession,
        filter_params: AuditQueryFilter,
        page: int = 1,
        page_size: int = 25,
    ) -> Tuple[List[AuditEvent], int]:
        query = select(AuditEvent)

        if filter_params.actor_id:
            query = query.where(AuditEvent.actor_id == filter_params.actor_id)
        if filter_params.action:
            query = query.where(AuditEvent.action == filter_params.action)
        if filter_params.resource_type:
            query = query.where(AuditEvent.resource_type == filter_params.resource_type)
        if filter_params.resource_id:
            query = query.where(AuditEvent.resource_id == filter_params.resource_id)
        if filter_params.correlation_id:
            query = query.where(AuditEvent.correlation_id == filter_params.correlation_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        offset = (page - 1) * page_size
        results = await session.scalars(
            query.order_by(AuditEvent.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(results.all()), total
