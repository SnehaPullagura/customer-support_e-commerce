"""
Knowledge Base Management, Article Publishing Lifecycle, and Full-Text Search Service.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.models.knowledge import (
    ArticleCategory,
    KnowledgeArticle,
    ArticleVersion,
    ArticleFeedback,
)
from app.schemas.knowledge import (
    ArticleCategoryCreate,
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    ArticleFeedbackCreate,
)


class KnowledgeService:
    @staticmethod
    async def create_category(session: AsyncSession, data: ArticleCategoryCreate) -> ArticleCategory:
        existing = await session.scalar(select(ArticleCategory).where(ArticleCategory.slug == data.slug.lower()))
        if existing:
            raise ConflictError(f"Category slug '{data.slug}' already exists.")

        cat = ArticleCategory(
            name=data.name,
            slug=data.slug.lower(),
            description=data.description,
            parent_id=data.parent_id,
            icon=data.icon,
            display_order=data.display_order,
        )
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return cat

    @staticmethod
    async def list_categories(session: AsyncSession) -> List[ArticleCategory]:
        res = await session.scalars(select(ArticleCategory).order_by(ArticleCategory.display_order))
        return list(res.all())

    @staticmethod
    async def create_article(
        session: AsyncSession, data: KnowledgeArticleCreate, author_id: str
    ) -> KnowledgeArticle:
        existing = await session.scalar(select(KnowledgeArticle).where(KnowledgeArticle.slug == data.slug.lower()))
        if existing:
            raise ConflictError(f"Article with slug '{data.slug}' already exists.")

        article = KnowledgeArticle(
            slug=data.slug.lower(),
            title=data.title,
            content=data.content,
            excerpt=data.excerpt or data.content[:200] + "...",
            category_id=data.category_id,
            visibility=data.visibility,
            tags=data.tags,
            author_id=author_id,
            status="DRAFT",
        )
        session.add(article)
        await session.flush()

        # Create version 1
        ver = ArticleVersion(
            article_id=article.id,
            version_number=1,
            title=article.title,
            content=article.content,
            changelog="Initial draft created",
            author_id=author_id,
        )
        session.add(ver)
        await session.commit()
        await session.refresh(article)
        return article

    @staticmethod
    async def publish_article(
        session: AsyncSession, article_id: str, reviewer_id: str
    ) -> KnowledgeArticle:
        article = await session.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
        if not article:
            raise EntityNotFoundError("KnowledgeArticle", article_id)

        article.status = "PUBLISHED"
        article.reviewed_by_id = reviewer_id
        article.published_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(article)
        return article

    @staticmethod
    async def get_article_by_slug(session: AsyncSession, slug: str) -> KnowledgeArticle:
        article = await session.scalar(
            select(KnowledgeArticle)
            .options(selectinload(KnowledgeArticle.category))
            .where(KnowledgeArticle.slug == slug.lower())
        )
        if not article:
            raise EntityNotFoundError("KnowledgeArticle", slug)

        # Increment view count
        article.view_count += 1
        await session.commit()
        return article

    @staticmethod
    async def search_articles(
        session: AsyncSession,
        query: str,
        category_id: Optional[str] = None,
        visibility: Optional[str] = "PUBLIC",
        limit: int = 10,
    ) -> List[KnowledgeArticle]:
        stmt = select(KnowledgeArticle).options(selectinload(KnowledgeArticle.category))
        
        if visibility:
            stmt = stmt.where(KnowledgeArticle.visibility == visibility)
        if category_id:
            stmt = stmt.where(KnowledgeArticle.category_id == category_id)

        if query:
            term = f"%{query}%"
            stmt = stmt.where(
                or_(
                    KnowledgeArticle.title.ilike(term),
                    KnowledgeArticle.content.ilike(term),
                    KnowledgeArticle.excerpt.ilike(term),
                )
            )

        res = await session.scalars(stmt.order_by(KnowledgeArticle.view_count.desc()).limit(limit))
        return list(res.all())

    @staticmethod
    async def submit_feedback(
        session: AsyncSession, article_id: str, data: ArticleFeedbackCreate, user_id: Optional[str] = None
    ) -> ArticleFeedback:
        article = await session.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id == article_id))
        if not article:
            raise EntityNotFoundError("KnowledgeArticle", article_id)

        fb = ArticleFeedback(
            article_id=article.id,
            is_helpful=data.is_helpful,
            user_id=user_id,
            comment=data.comment,
        )
        session.add(fb)

        if data.is_helpful:
            article.helpful_votes += 1
        else:
            article.unhelpful_votes += 1

        await session.commit()
        await session.refresh(fb)
        return fb
