"""
Common shared schemas, pagination envelopes, and generic responses.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class StandardResponse(BaseSchema, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class ErrorDetail(BaseSchema):
    field: Optional[str] = None
    issue: str
    code: Optional[str] = None


class ProblemDetails(BaseSchema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    error_code: str = "ERROR"
    errors: Optional[List[ErrorDetail]] = None
