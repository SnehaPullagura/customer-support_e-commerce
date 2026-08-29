"""
Knowledge Base, Article Lifecycle, Versioning, Categories, and Feedback models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class ArticleCategory(BaseEntity):
    __tablename__ = "article_categories"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("article_categories.id", ondelete="SET NULL"), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    articles: Mapped[List["KnowledgeArticle"]] = relationship("KnowledgeArticle", back_populates="category")


class KnowledgeArticle(BaseEntity):
    __tablename__ = "knowledge_articles"

    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("article_categories.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)
    # DRAFT, REVIEW, APPROVED, PUBLISHED, ARCHIVED
    
    visibility: Mapped[str] = mapped_column(String(50), default="PUBLIC", nullable=False)  # PUBLIC (Customer), INTERNAL (Staff only), VIP
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reviewed_by_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    helpful_votes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unhelpful_votes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    category: Mapped[Optional["ArticleCategory"]] = relationship("ArticleCategory", back_populates="articles")
    versions: Mapped[List["ArticleVersion"]] = relationship("ArticleVersion", back_populates="article", cascade="all, delete-orphan")
    feedbacks: Mapped[List["ArticleFeedback"]] = relationship("ArticleFeedback", back_populates="article", cascade="all, delete-orphan")


class ArticleVersion(BaseEntity):
    __tablename__ = "article_versions"

    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    changelog: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)

    article: Mapped["KnowledgeArticle"] = relationship("KnowledgeArticle", back_populates="versions")


class ArticleFeedback(BaseEntity):
    __tablename__ = "article_feedbacks"

    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    is_helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    article: Mapped["KnowledgeArticle"] = relationship("KnowledgeArticle", back_populates="feedbacks")
