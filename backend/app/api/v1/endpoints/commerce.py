"""
Commerce Integration endpoints providing real-time queries to Orders, Shipments, Payments, and Commerce Graph.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query

from app.adapters.commerce import get_commerce_adapter
from app.core.dependencies import get_current_user, CurrentUser
from app.schemas.commerce import (
    CommerceOrderDTO,
    CommerceCustomerDTO,
    CommercePaymentDTO,
    CommerceShipmentDTO,
    CommerceGraphDTO,
)
from app.schemas.common import StandardResponse

router = APIRouter()


@router.get("/orders/{order_id}", response_model=StandardResponse[CommerceOrderDTO])
async def get_order_details(
    order_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    commerce = get_commerce_adapter()
    order = await commerce.get_order(order_id)
    if not order:
        return StandardResponse(success=False, message="Order not found in commerce system", data=None)
    return StandardResponse(data=order)


@router.get("/customers/{customer_id}/orders", response_model=StandardResponse[List[CommerceOrderDTO]])
async def get_customer_orders(
    customer_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    limit: int = Query(10, ge=1, le=50),
):
    commerce = get_commerce_adapter()
    orders = await commerce.get_customer_orders(customer_id, limit=limit)
    return StandardResponse(data=orders)


@router.get("/graph", response_model=StandardResponse[CommerceGraphDTO])
async def get_commerce_graph(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    customer_id: Optional[str] = None,
    order_id: Optional[str] = None,
):
    commerce = get_commerce_adapter()
    graph = await commerce.get_commerce_graph(external_customer_id=customer_id, order_id=order_id)
    return StandardResponse(data=graph)
