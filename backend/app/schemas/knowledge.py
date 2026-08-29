"""
Knowledge Base Categories, Articles, and Feedback schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import Field

from app.schemas.common import BaseSchema


class ArticleCategoryCreate(BaseSchema):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0


class ArticleCategoryResponse(BaseSchema):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    display_order: int
    created_at: datetime


class KnowledgeArticleCreate(BaseSchema):
    title: str = Field(..., min_length=3, max_length=255)
    slug: str
    content: str = Field(..., min_length=10)
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    visibility: str = "PUBLIC"
    tags: List[str] = []


class KnowledgeArticleUpdate(BaseSchema):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    status: Optional[str] = None
    visibility: Optional[str] = None
    tags: Optional[List[str]] = None
    changelog: Optional[str] = None


class ArticleFeedbackCreate(BaseSchema):
    is_helpful: bool
    comment: Optional[str] = None


class KnowledgeArticleResponse(BaseSchema):
    id: str
    slug: str
    title: str
    content: str
    excerpt: Optional[str] = None
    category_id: Optional[str] = None
    status: str
    visibility: str
    tags: List[str]
    author_id: str
    view_count: int
    helpful_votes: int
    unhelpful_votes: int
    published_at: Optional[datetime] = None
    category: Optional[ArticleCategoryResponse] = None
    created_at: datetime
    updated_at: datetime


class ArticleSearchQuery(BaseSchema):
    query: str
    category_id: Optional[str] = None
    visibility: Optional[str] = "PUBLIC"
    limit: int = 10
