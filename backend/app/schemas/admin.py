"""
Admin System Settings and Feature Flag schemas.
"""

from typing import Optional
from app.schemas.common import BaseSchema


class SystemSettingUpdate(BaseSchema):
    value: str
    description: Optional[str] = None


class SystemSettingResponse(BaseSchema):
    id: str
    key: str
    value: str
    value_type: str
    description: Optional[str] = None
    is_public: bool


class FeatureFlagCreate(BaseSchema):
    name: str
    description: Optional[str] = None
    is_enabled: bool = False
    rollout_percentage: int = 100
    target_segments: Optional[dict] = None


class FeatureFlagResponse(BaseSchema):
    id: str
    name: str
    description: Optional[str] = None
    is_enabled: bool
    rollout_percentage: int
    target_segments: Optional[dict] = None
