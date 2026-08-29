"""
Knowledge Base endpoints.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag import VectorRAGService
from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.knowledge import (
    ArticleCategoryCreate,
    ArticleCategoryResponse,
    KnowledgeArticleCreate,
    KnowledgeArticleResponse,
    ArticleFeedbackCreate,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.post("/categories", response_model=StandardResponse[ArticleCategoryResponse], status_code=status.HTTP_201_CREATED)
async def create_category(
    data: ArticleCategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    cat = await KnowledgeService.create_category(db, data)
    return StandardResponse(message="Category created", data=ArticleCategoryResponse.model_validate(cat))


@router.get("/categories", response_model=StandardResponse[List[ArticleCategoryResponse]])
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    cats = await KnowledgeService.list_categories(db)
    return StandardResponse(data=[ArticleCategoryResponse.model_validate(c) for c in cats])


@router.post("/articles", response_model=StandardResponse[KnowledgeArticleResponse], status_code=status.HTTP_201_CREATED)
async def create_article(
    data: KnowledgeArticleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    art = await KnowledgeService.create_article(db, data, author_id=current_user.user_id)
    return StandardResponse(message="Article created in draft state", data=KnowledgeArticleResponse.model_validate(art))


@router.get("/articles", response_model=StandardResponse[List[KnowledgeArticleResponse]])
async def search_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query("", description="Search term"),
    category_id: Optional[str] = None,
    visibility: Optional[str] = "PUBLIC",
    limit: int = Query(10, ge=1, le=50),
):
    articles = await KnowledgeService.search_articles(
        db, query=query, category_id=category_id, visibility=visibility, limit=limit
    )
    return StandardResponse(data=[KnowledgeArticleResponse.model_validate(a) for a in articles])


@router.get("/articles/{slug}", response_model=StandardResponse[KnowledgeArticleResponse])
async def get_article(slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    article = await KnowledgeService.get_article_by_slug(db, slug)
    return StandardResponse(data=KnowledgeArticleResponse.model_validate(article))


@router.post("/articles/{article_id}/publish", response_model=StandardResponse[KnowledgeArticleResponse])
async def publish_article(
    article_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    art = await KnowledgeService.publish_article(db, article_id, reviewer_id=current_user.user_id)
    # Auto-index into vector RAG store
    await VectorRAGService.index_knowledge_article(db, art)
    return StandardResponse(message="Article published and indexed into Vector RAG", data=KnowledgeArticleResponse.model_validate(art))


@router.post("/articles/{article_id}/feedback", response_model=StandardResponse[dict])
async def submit_article_feedback(
    article_id: str,
    data: ArticleFeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    fb = await KnowledgeService.submit_feedback(db, article_id, data)
    return StandardResponse(message="Thank you for your feedback!", data={"feedback_id": fb.id})
