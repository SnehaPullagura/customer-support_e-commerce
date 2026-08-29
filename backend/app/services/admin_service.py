"""
Administration Service for System Settings and Feature Flags.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.admin import SystemSetting, FeatureFlag
from app.schemas.admin import FeatureFlagCreate


class AdminService:
    @staticmethod
    async def set_system_setting(
        session: AsyncSession, key: str, value: str, value_type: str = "STRING", description: Optional[str] = None
    ) -> SystemSetting:
        setting = await session.scalar(select(SystemSetting).where(SystemSetting.key == key))
        if not setting:
            setting = SystemSetting(
                key=key,
                value=value,
                value_type=value_type,
                description=description,
            )
            session.add(setting)
        else:
            setting.value = value
            if description:
                setting.description = description

        await session.commit()
        await session.refresh(setting)
        return setting

    @staticmethod
    async def get_system_settings(session: AsyncSession) -> List[SystemSetting]:
        res = await session.scalars(select(SystemSetting).order_by(SystemSetting.key))
        return list(res.all())

    @staticmethod
    async def create_feature_flag(session: AsyncSession, data: FeatureFlagCreate) -> FeatureFlag:
        flag = FeatureFlag(
            name=data.name,
            description=data.description,
            is_enabled=data.is_enabled,
            rollout_percentage=data.rollout_percentage,
            target_segments=data.target_segments,
        )
        session.add(flag)
        await session.commit()
        await session.refresh(flag)
        return flag

    @staticmethod
    async def list_feature_flags(session: AsyncSession) -> List[FeatureFlag]:
        res = await session.scalars(select(FeatureFlag).order_by(FeatureFlag.name))
        return list(res.all())
