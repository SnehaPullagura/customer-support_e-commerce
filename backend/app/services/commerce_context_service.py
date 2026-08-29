"""
Commerce Context Aggregator and Unified Graph Service.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.adapters.commerce import get_commerce_adapter
from app.core.redis import redis_manager
from app.models.case import Case
from app.models.customer import Customer
from app.schemas.commerce import CommerceGraphDTO


class CommerceContextService:
    @staticmethod
    async def get_case_commerce_context(
        session: AsyncSession, case_id: str, use_cache: bool = True
    ) -> CommerceGraphDTO:
        cache_key = f"commerce_graph:case:{case_id}"
        if use_cache:
            cached = await redis_manager.get_json(cache_key)
            if cached:
                return CommerceGraphDTO(**cached)

        case = await session.scalar(select(Case).where(Case.id == case_id))
        if not case:
            return CommerceGraphDTO()

        customer = await session.scalar(select(Customer).where(Customer.id == case.customer_id))
        ext_cust_id = customer.external_customer_id if customer else None

        commerce = get_commerce_adapter()
        graph = await commerce.get_commerce_graph(
            external_customer_id=ext_cust_id,
            order_id=case.order_id,
        )

        # Cache for 60 seconds
        await redis_manager.set_json(cache_key, graph.model_dump(mode="json"), expire_seconds=60)
        return graph

    @staticmethod
    async def get_customer_commerce_context(
        session: AsyncSession, customer_id: str
    ) -> CommerceGraphDTO:
        customer = await session.scalar(select(Customer).where(Customer.id == customer_id))
        if not customer or not customer.external_customer_id:
            return CommerceGraphDTO()

        commerce = get_commerce_adapter()
        return await commerce.get_commerce_graph(external_customer_id=customer.external_customer_id)
