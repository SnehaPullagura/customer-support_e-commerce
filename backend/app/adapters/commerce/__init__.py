"""
Commerce Adapter Factory and Module exports.
"""

from typing import Optional
from app.adapters.commerce.base import CommerceAdapter
from app.adapters.commerce.mock_adapter import MockCommerceAdapter
from app.adapters.commerce.rest_adapter import RestCommerceAdapter
from app.core.config import settings

_commerce_adapter_instance: Optional[CommerceAdapter] = None


def get_commerce_adapter() -> CommerceAdapter:
    """Factory dependency returning the configured singleton Commerce Adapter."""
    global _commerce_adapter_instance
    if _commerce_adapter_instance is None:
        if settings.COMMERCE_ADAPTER_TYPE == "rest":
            _commerce_adapter_instance = RestCommerceAdapter()
        else:
            _commerce_adapter_instance = MockCommerceAdapter()
    return _commerce_adapter_instance


__all__ = [
    "CommerceAdapter",
    "MockCommerceAdapter",
    "RestCommerceAdapter",
    "get_commerce_adapter",
]
