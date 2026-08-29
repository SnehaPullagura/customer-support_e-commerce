"""
Customer Self-Service endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.commerce import get_commerce_adapter
from app.core.database import get_db
from app.models.self_service import TroubleshootingFlow
from app.schemas.commerce import CommerceOrderDTO
from app.schemas.common import StandardResponse
from app.schemas.self_service import (
    TroubleshootingFlowResponse,
    SelfServiceStepRequest,
    SelfServiceResponse,
)
from app.services.self_service_service import SelfServiceService

router = APIRouter()


@router.get("/flows", response_model=StandardResponse[List[TroubleshootingFlowResponse]])
async def list_troubleshooting_flows(db: Annotated[AsyncSession, Depends(get_db)]):
    flows = await SelfServiceService.list_flows(db)
    return StandardResponse(data=[TroubleshootingFlowResponse.model_validate(f) for f in flows])


@router.post("/step", response_model=StandardResponse[SelfServiceResponse])
async def execute_troubleshooting_step(
    data: SelfServiceStepRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    resp = await SelfServiceService.execute_step(db, data)
    return StandardResponse(data=resp)


@router.get("/track-order/{order_id}", response_model=StandardResponse[dict])
async def track_order_self_service(order_id: str):
    commerce = get_commerce_adapter()
    order = await commerce.get_order(order_id)
    if not order:
        return StandardResponse(success=False, message="Order not found", data=None)

    tracking_data = {
        "order_id": order.order_id,
        "status": order.status,
        "placed_at": order.placed_at.isoformat(),
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "items": [it.model_dump(mode="json") for it in order.items],
        "shipments": [s.model_dump(mode="json") for s in order.shipments],
    }
    return StandardResponse(message="Order tracking details retrieved", data=tracking_data)
