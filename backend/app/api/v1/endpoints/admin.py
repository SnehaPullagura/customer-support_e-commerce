"""
Admin Settings and Feature Flags endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.schemas.admin import (
    SystemSettingUpdate,
    SystemSettingResponse,
    FeatureFlagCreate,
    FeatureFlagResponse,
)
from app.schemas.common import StandardResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/settings", response_model=StandardResponse[List[SystemSettingResponse]])
async def list_system_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
):
    settings_list = await AdminService.get_system_settings(db)
    return StandardResponse(data=[SystemSettingResponse.model_validate(s) for s in settings_list])


@router.put("/settings/{key}", response_model=StandardResponse[SystemSettingResponse])
async def update_system_setting(
    key: str,
    data: SystemSettingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
):
    setting = await AdminService.set_system_setting(db, key=key, value=data.value, description=data.description)
    return StandardResponse(message="System setting saved", data=SystemSettingResponse.model_validate(setting))


@router.post("/feature-flags", response_model=StandardResponse[FeatureFlagResponse], status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    data: FeatureFlagCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.ADMINISTRATORS))],
):
    flag = await AdminService.create_feature_flag(db, data)
    return StandardResponse(message="Feature flag created", data=FeatureFlagResponse.model_validate(flag))


@router.get("/feature-flags", response_model=StandardResponse[List[FeatureFlagResponse]])
async def list_feature_flags(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    flags = await AdminService.list_feature_flags(db)
    return StandardResponse(data=[FeatureFlagResponse.model_validate(f) for f in flags])
