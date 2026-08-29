"""
Customer Management Service.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.exceptions import EntityNotFoundError, ConflictError
from app.models.customer import Customer, CustomerPreference, CustomerTag, CustomerTimelineEvent
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPreferenceUpdate


class CustomerService:
    @staticmethod
    async def create_customer(session: AsyncSession, data: CustomerCreate) -> Customer:
        existing = await session.scalar(select(Customer).where(Customer.email == data.email.lower()))
        if existing:
            raise ConflictError(f"Customer with email '{data.email}' already exists.")

        customer = Customer(
            user_id=data.user_id,
            external_customer_id=data.external_customer_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email.lower(),
            phone=data.phone,
            preferred_language=data.preferred_language,
            segment=data.segment,
            tier=data.tier,
            notes=data.notes,
        )
        session.add(customer)
        await session.flush()

        # Default preferences
        pref = CustomerPreference(
            customer_id=customer.id,
            email_notifications=True,
            sms_notifications=bool(customer.phone),
            preferred_channel="EMAIL",
        )
        session.add(pref)

        # Initial timeline event
        event = CustomerTimelineEvent(
            customer_id=customer.id,
            event_type="CUSTOMER_CREATED",
            title="Customer profile created",
            description="Customer registered into the support ecosystem.",
        )
        session.add(event)
        await session.commit()
        await session.refresh(customer)
        return customer

    @staticmethod
    async def get_customer(session: AsyncSession, customer_id: str) -> Customer:
        customer = await session.scalar(
            select(Customer)
            .options(
                selectinload(Customer.preference),
                selectinload(Customer.tags),
                selectinload(Customer.timeline_events),
            )
            .where(Customer.id == customer_id)
        )
        if not customer:
            raise EntityNotFoundError("Customer", customer_id)
        return customer

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: str) -> Optional[Customer]:
        return await session.scalar(
            select(Customer)
            .options(selectinload(Customer.preference), selectinload(Customer.tags))
            .where(Customer.user_id == user_id)
        )

    @staticmethod
    async def list_customers(
        session: AsyncSession,
        search: Optional[str] = None,
        segment: Optional[str] = None,
        tier: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Customer], int]:
        query = select(Customer).options(selectinload(Customer.tags))

        if search:
            term = f"%{search}%"
            query = query.where(
                or_(
                    Customer.first_name.ilike(term),
                    Customer.last_name.ilike(term),
                    Customer.email.ilike(term),
                    Customer.phone.ilike(term),
                    Customer.external_customer_id.ilike(term),
                )
            )
        if segment:
            query = query.where(Customer.segment == segment)
        if tier:
            query = query.where(Customer.tier == tier)

        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0

        offset = (page - 1) * page_size
        results = await session.scalars(
            query.order_by(Customer.created_at.desc()).offset(offset).limit(page_size)
        )
        return list(results.all()), total

    @staticmethod
    async def update_customer(session: AsyncSession, customer_id: str, data: CustomerUpdate) -> Customer:
        customer = await CustomerService.get_customer(session, customer_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)

        event = CustomerTimelineEvent(
            customer_id=customer.id,
            event_type="PROFILE_UPDATED",
            title="Profile details updated",
            description=f"Fields updated: {', '.join(update_data.keys())}",
        )
        session.add(event)
        await session.commit()
        await session.refresh(customer)
        return customer

    @staticmethod
    async def update_preferences(
        session: AsyncSession, customer_id: str, data: CustomerPreferenceUpdate
    ) -> CustomerPreference:
        pref = await session.scalar(
            select(CustomerPreference).where(CustomerPreference.customer_id == customer_id)
        )
        if not pref:
            pref = CustomerPreference(customer_id=customer_id)
            session.add(pref)

        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(pref, key, val)

        await session.commit()
        await session.refresh(pref)
        return pref

    @staticmethod
    async def add_tag(session: AsyncSession, customer_id: str, tag_name: str, color: str = "#6B7280") -> CustomerTag:
        customer = await CustomerService.get_customer(session, customer_id)
        tag = CustomerTag(customer_id=customer.id, tag_name=tag_name.strip().upper(), color=color)
        customer.tags.append(tag)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
        return tag

    @staticmethod
    async def add_timeline_event(
        session: AsyncSession,
        customer_id: str,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        reference_id: Optional[str] = None,
        metadata_json: Optional[dict] = None,
    ) -> CustomerTimelineEvent:
        event = CustomerTimelineEvent(
            customer_id=customer_id,
            event_type=event_type,
            title=title,
            description=description,
            reference_id=reference_id,
            metadata_json=metadata_json,
        )
        session.add(event)
        await session.commit()
        return event
