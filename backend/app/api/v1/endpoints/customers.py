"""
Customer Management endpoints.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse, PaginatedResponse
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerDetailResponse,
    CustomerPreferenceUpdate,
    CustomerPreferenceResponse,
    CustomerTagResponse,
)
from app.schemas.commerce import CommerceGraphDTO
from app.services.customer_service import CustomerService
from app.services.commerce_context_service import CommerceContextService

router = APIRouter()


@router.post("", response_model=StandardResponse[CustomerResponse], status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    cust = await CustomerService.create_customer(db, data)
    return StandardResponse(
        message="Customer created successfully",
        data=CustomerResponse.model_validate(cust),
    )


@router.get("", response_model=StandardResponse[PaginatedResponse[CustomerResponse]])
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    search: Optional[str] = None,
    segment: Optional[str] = None,
    tier: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await CustomerService.list_customers(
        db, search=search, segment=segment, tier=tier, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    paginated = PaginatedResponse[CustomerResponse](
        items=[CustomerResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return StandardResponse(data=paginated)


@router.get("/{customer_id}", response_model=StandardResponse[CustomerDetailResponse])
async def get_customer(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    cust = await CustomerService.get_customer(db, customer_id)
    return StandardResponse(data=CustomerDetailResponse.model_validate(cust))


@router.patch("/{customer_id}", response_model=StandardResponse[CustomerResponse])
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    cust = await CustomerService.update_customer(db, customer_id, data)
    return StandardResponse(
        message="Customer updated successfully",
        data=CustomerResponse.model_validate(cust),
    )


@router.put("/{customer_id}/preferences", response_model=StandardResponse[CustomerPreferenceResponse])
async def update_preferences(
    customer_id: str,
    data: CustomerPreferenceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    pref = await CustomerService.update_preferences(db, customer_id, data)
    return StandardResponse(
        message="Customer preferences updated",
        data=CustomerPreferenceResponse.model_validate(pref),
    )


@router.post("/{customer_id}/tags", response_model=StandardResponse[CustomerTagResponse])
async def add_tag(
    customer_id: str,
    tag_name: str,
    color: str = "#6B7280",
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))] = None,
):
    tag = await CustomerService.add_tag(db, customer_id, tag_name=tag_name, color=color)
    return StandardResponse(
        message="Tag added to customer",
        data=CustomerTagResponse.model_validate(tag),
    )


@router.get("/{customer_id}/commerce-context", response_model=StandardResponse[CommerceGraphDTO])
async def get_customer_commerce_context(
    customer_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    graph = await CommerceContextService.get_customer_commerce_context(db, customer_id)
    return StandardResponse(data=graph)
